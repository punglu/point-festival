/**
 * 마크포인트 관리 화면 — service administration, not family administration.
 *
 * The single most important rule on this screen: **holding the family is not
 * holding the service.** `markpoint.missions.manage` and
 * `markpoint.points.adjust` are separate permissions that no FAMILY-scope role
 * carries, and the two panels below are gated independently. A family owner
 * with neither permission sees neither panel — and if they somehow reached the
 * route, every request the panels make is refused server-side anyway. The
 * frontend gate is convenience; the server gate is the contract.
 *
 * Bulk approval is **all-or-nothing** by product contract. When the server
 * refuses a batch it changes nothing, so this screen must not render a partial
 * result — a UI that showed "3 of 5 approved" after a full rollback would be
 * describing a state that never existed.
 */
import { useCallback, useEffect, useMemo, useState } from 'react';

import {
  adjustPoints,
  bulkApproveMissions,
  correctDeduction,
  getCycleConfig,
  listMissions,
  listTemplates,
  materializeWindow,
  rejectMission,
  updateCycleConfig,
  MISSION_STATUS_LABEL,
  type AdminMissionFilters,
  type MarkpointCycleConfig,
  type MarkpointMission,
  type MarkpointTemplate,
  type MissionStatus,
} from '../../shared/api/markpointApi';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './MarkpointAdmin.module.css';

const STATUSES: MissionStatus[] = [
  'active',
  'pending_approval',
  'completed',
  'rejected',
  'cancelled',
  'expired',
];

const CYCLES = ['daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly'];

type Banner = { tone: 'ok' | 'warn' | 'error'; text: string } | null;

export function MarkpointAdmin() {
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const can = useFamilyContextStore((s) => s.can);
  const canManageMissions = can('markpoint.missions.manage');
  const canAdjustPoints = can('markpoint.points.adjust');

  const [missions, setMissions] = useState<MarkpointMission[]>([]);
  const [templates, setTemplates] = useState<MarkpointTemplate[]>([]);
  const [config, setConfig] = useState<MarkpointCycleConfig | null>(null);
  const [filters, setFilters] = useState<AdminMissionFilters>({});
  const [selected, setSelected] = useState<number[]>([]);
  const [banner, setBanner] = useState<Banner>(null);
  const [loading, setLoading] = useState(false);

  const loadMissions = useCallback(
    async (familyId: number, next: AdminMissionFilters, signal?: AbortSignal) => {
      setLoading(true);
      try {
        const rows = await listMissions(familyId, next, signal);
        setMissions(rows);
        // Drop selections that the new filter no longer shows — approving a
        // mission the admin can no longer see would be acting blind.
        setSelected((prev) => prev.filter((id) => rows.some((m) => m.id === id)));
      } catch {
        if (signal?.aborted) return;
        setBanner({ tone: 'error', text: '미션 목록을 불러오지 못했어요.' });
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    if (activeFamilyId === null || !canManageMissions) return undefined;
    const controller = new AbortController();
    void loadMissions(activeFamilyId, filters, controller.signal);
    void listTemplates(activeFamilyId, controller.signal).then(setTemplates).catch(() => undefined);
    void getCycleConfig(activeFamilyId, controller.signal).then(setConfig).catch(() => undefined);
    return () => controller.abort();
  }, [activeFamilyId, canManageMissions, filters, loadMissions]);

  const pendingIds = useMemo(
    () => missions.filter((m) => m.status === 'pending_approval').map((m) => m.id),
    [missions],
  );

  if (activeFamilyId === null) {
    return (
      <section className={styles.page}>
        <h1>가족을 선택해주세요</h1>
      </section>
    );
  }

  // Neither permission: the route is reachable but there is nothing here for
  // this account. Stated plainly rather than shown as an empty screen.
  if (!canManageMissions && !canAdjustPoints) {
    return (
      <section className={styles.page} role="alert" data-testid="markpoint-admin-denied">
        <h1>마크포인트 관리 권한이 없어요</h1>
        <p className={styles.muted}>
          가족 관리자 권한과 마크포인트 서비스 관리자 권한은 서로 다릅니다. 서비스 관리자
          권한을 부여받은 뒤 다시 시도해주세요.
        </p>
      </section>
    );
  }

  const applyFilter = (patch: AdminMissionFilters) =>
    setFilters((prev) => {
      const next = { ...prev, ...patch };
      Object.keys(next).forEach((k) => {
        const key = k as keyof AdminMissionFilters;
        if (next[key] === undefined || next[key] === ('' as never)) delete next[key];
      });
      return next;
    });

  const handleBulkApprove = async () => {
    if (selected.length === 0) return;
    setBanner(null);
    try {
      const result = await bulkApproveMissions(activeFamilyId, selected);
      setBanner({
        tone: 'ok',
        text: `${result.approved.length}건을 승인했어요.${
          result.skipped_already_completed.length
            ? ` (이미 완료 ${result.skipped_already_completed.length}건 건너뜀)`
            : ''
        }`,
      });
      setSelected([]);
      await loadMissions(activeFamilyId, filters);
    } catch (error: unknown) {
      const response = (error as { response?: { status?: number; data?: { detail?: string } } })
        .response;
      // The batch is atomic: on refusal nothing was approved. Say so, rather
      // than leaving the admin to guess which half landed.
      setBanner({
        tone: 'error',
        text:
          response?.status === 409 || response?.status === 404
            ? `일괄 승인이 취소되었습니다 — 아무 미션도 승인되지 않았어요. ${
                response?.data?.detail ?? ''
              }`
            : '일괄 승인에 실패했어요. 아무 미션도 승인되지 않았습니다.',
      });
      await loadMissions(activeFamilyId, filters);
    }
  };

  const handleMaterialize = async () => {
    setBanner(null);
    try {
      const result = await materializeWindow(activeFamilyId);
      setBanner({
        tone: 'ok',
        text: `${result.window_start} ~ ${result.window_end} 기간에 미션 ${result.missions_created}건을 생성했어요. (기존 ${result.missions_skipped_existing}건 유지)`,
      });
      await loadMissions(activeFamilyId, filters);
    } catch {
      setBanner({ tone: 'error', text: '미션 생성에 실패했어요.' });
    }
  };

  const handleCycleChange = async (cycleType: string) => {
    setBanner(null);
    try {
      const next = await updateCycleConfig(activeFamilyId, { cycle_type: cycleType });
      setConfig(next);
      setBanner({ tone: 'ok', text: `주기를 ${cycleType}(으)로 변경했어요.` });
    } catch (error: unknown) {
      const response = (error as { response?: { status?: number; data?: { detail?: string } } })
        .response;
      // Guard A and Guard B are meaningful refusals, not generic errors. The
      // server's message carries the remaining days or the template count,
      // which is the only thing that makes the refusal actionable.
      setBanner({
        tone: response?.status === 409 ? 'warn' : 'error',
        text: response?.data?.detail ?? '주기를 변경하지 못했어요.',
      });
    }
  };

  return (
    <section className={styles.page} aria-labelledby="markpoint-admin-title">
      <header className={styles.header}>
        <p className={styles.eyebrow}>몽글 · 마크포인트 관리</p>
        <h1 id="markpoint-admin-title">마크포인트 관리</h1>
      </header>

      {banner && (
        <p className={`${styles.banner} ${styles[banner.tone]}`} role="alert" data-testid="markpoint-admin-banner">
          {banner.text}
        </p>
      )}

      {canManageMissions && (
        <>
          <section className={styles.block} aria-labelledby="mp-admin-config">
            <h2 id="mp-admin-config">운영 주기</h2>
            <div className={styles.row}>
              <label htmlFor="cycle-select">주기</label>
              <select
                id="cycle-select"
                className={styles.select}
                value={config?.cycle_type ?? 'weekly'}
                onChange={(e) => void handleCycleChange(e.target.value)}
                data-testid="cycle-select"
              >
                {CYCLES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
              <span className={styles.muted}>
                {config?.effective_from} ~ {config?.effective_to}
              </span>
            </div>
            {/* No force override control exists: no approved contract defines
                one, and an override is where a guard quietly stops meaning
                anything. */}
          </section>

          <section className={styles.block} aria-labelledby="mp-admin-templates">
            <h2 id="mp-admin-templates">반복 미션 템플릿</h2>
            <div className={styles.row}>
              <span className={styles.muted}>활성 템플릿 {templates.length}건</span>
              <button
                type="button"
                className={styles.secondary}
                onClick={() => void handleMaterialize()}
                data-testid="materialize-window"
              >
                이번 주기 미션 생성
              </button>
            </div>
          </section>

          <section className={styles.block} aria-labelledby="mp-admin-missions">
            <h2 id="mp-admin-missions">미션</h2>

            <div className={styles.filters} role="group" aria-label="미션 필터">
              <label className={styles.filterField}>
                <span>상태</span>
                <select
                  className={styles.select}
                  value={filters.mission_status ?? ''}
                  onChange={(e) =>
                    applyFilter({ mission_status: (e.target.value || undefined) as MissionStatus })
                  }
                  data-testid="filter-status"
                >
                  <option value="">전체</option>
                  {STATUSES.map((s) => (
                    <option key={s} value={s}>
                      {MISSION_STATUS_LABEL[s]}
                    </option>
                  ))}
                </select>
              </label>
              <label className={styles.filterField}>
                <span>시작일</span>
                <input
                  type="date"
                  className={styles.input}
                  value={filters.date_from ?? ''}
                  onChange={(e) => applyFilter({ date_from: e.target.value || undefined })}
                  data-testid="filter-date-from"
                />
              </label>
              <label className={styles.filterField}>
                <span>종료일</span>
                <input
                  type="date"
                  className={styles.input}
                  value={filters.date_to ?? ''}
                  onChange={(e) => applyFilter({ date_to: e.target.value || undefined })}
                  data-testid="filter-date-to"
                />
              </label>
            </div>

            <div className={styles.row}>
              <button
                type="button"
                className={styles.secondary}
                onClick={() => setSelected(pendingIds)}
                disabled={pendingIds.length === 0}
                data-testid="select-all-pending"
              >
                승인 대기 전체 선택 ({pendingIds.length})
              </button>
              <button
                type="button"
                className={styles.primary}
                onClick={() => void handleBulkApprove()}
                disabled={selected.length === 0}
                data-testid="bulk-approve"
              >
                선택 {selected.length}건 일괄 승인
              </button>
            </div>
            <p className={styles.muted}>
              일괄 승인은 전부 성공하거나 전부 취소됩니다. 일부만 승인되는 경우는 없습니다.
            </p>

            {loading ? (
              <p className={styles.muted} aria-busy="true">
                불러오는 중…
              </p>
            ) : missions.length === 0 ? (
              <p className={styles.empty} data-testid="admin-missions-empty">
                조건에 맞는 미션이 없어요.
              </p>
            ) : (
              <div className={styles.tableScroll}>
                <table className={styles.table} data-testid="admin-mission-table">
                  <caption className={styles.srOnly}>미션 목록</caption>
                  <thead>
                    <tr>
                      <th scope="col">선택</th>
                      <th scope="col">날짜</th>
                      <th scope="col">제목</th>
                      <th scope="col">보상</th>
                      <th scope="col">상태</th>
                      <th scope="col">작업</th>
                    </tr>
                  </thead>
                  <tbody>
                    {missions.map((mission) => (
                      <tr key={mission.id} data-mission-id={mission.id}>
                        <td>
                          <input
                            type="checkbox"
                            aria-label={`${mission.title} 선택`}
                            checked={selected.includes(mission.id)}
                            disabled={mission.status !== 'pending_approval'}
                            onChange={(e) =>
                              setSelected((prev) =>
                                e.target.checked
                                  ? [...prev, mission.id]
                                  : prev.filter((id) => id !== mission.id),
                              )
                            }
                            data-testid={`select-mission-${mission.id}`}
                          />
                        </td>
                        <td>{mission.scheduled_for}</td>
                        <td>{mission.title}</td>
                        <td>{mission.reward_amount}</td>
                        <td>
                          <span className={styles.badge} data-status={mission.status}>
                            {MISSION_STATUS_LABEL[mission.status as MissionStatus] ?? mission.status}
                          </span>
                        </td>
                        <td>
                          {mission.status === 'pending_approval' && (
                            <button
                              type="button"
                              className={styles.linkButton}
                              onClick={async () => {
                                await rejectMission(activeFamilyId, mission.id, '반려');
                                await loadMissions(activeFamilyId, filters);
                              }}
                              data-testid={`reject-mission-${mission.id}`}
                            >
                              반려
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}

      {/* Rendered only for `markpoint.points.adjust`. A mission manager must
          not see a point-adjustment control, and vice versa — the two are
          separate authorities, not two views of one admin role. */}
      {canAdjustPoints && (
        <PointAdjustmentPanel familyId={activeFamilyId} onDone={setBanner} />
      )}
    </section>
  );
}

function PointAdjustmentPanel({
  familyId,
  onDone,
}: {
  familyId: number;
  onDone: (banner: Banner) => void;
}) {
  const [membershipId, setMembershipId] = useState('');
  const [amount, setAmount] = useState('');
  const [reason, setReason] = useState('');
  const [entryId, setEntryId] = useState('');
  const [newAmount, setNewAmount] = useState('');

  const submitAdjustment = async () => {
    try {
      await adjustPoints(familyId, {
        beneficiary_membership_id: Number(membershipId),
        amount: Number(amount),
        reason,
        // Idempotency key is generated per submission so a double-click cannot
        // create a second ledger entry.
        idempotency_key:
          typeof crypto !== 'undefined' && 'randomUUID' in crypto
            ? crypto.randomUUID()
            : `adj-${Date.now()}`,
      });
      onDone({ tone: 'ok', text: '포인트를 조정했어요.' });
      setAmount('');
      setReason('');
    } catch (error: unknown) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      onDone({ tone: 'error', text: detail ?? '포인트 조정에 실패했어요.' });
    }
  };

  const submitCorrection = async () => {
    try {
      const result = await correctDeduction(familyId, Number(entryId), {
        new_amount: newAmount === '' ? null : Number(newAmount),
        reason: reason || '정정',
      });
      onDone({
        tone: 'ok',
        // Worded as append-only on purpose: the original entry still exists.
        text: `#${result.original_entry_id} 차감을 취소하고${
          result.replacement_entry_id ? ' 새 차감을 추가' : ''
        }했어요. 원본 기록은 그대로 남습니다.`,
      });
      setEntryId('');
      setNewAmount('');
    } catch (error: unknown) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      onDone({ tone: 'error', text: detail ?? '차감 정정에 실패했어요.' });
    }
  };

  return (
    <section className={styles.block} aria-labelledby="mp-admin-points" data-testid="point-adjust-panel">
      <h2 id="mp-admin-points">포인트 조정</h2>
      <div className={styles.formGrid}>
        <label className={styles.filterField}>
          <span>구성원 ID</span>
          <input
            className={styles.input}
            value={membershipId}
            onChange={(e) => setMembershipId(e.target.value)}
            inputMode="numeric"
            data-testid="adjust-membership"
          />
        </label>
        <label className={styles.filterField}>
          <span>포인트 (음수는 차감)</span>
          <input
            className={styles.input}
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            inputMode="numeric"
            data-testid="adjust-amount"
          />
        </label>
        <label className={styles.filterField}>
          <span>사유</span>
          <input
            className={styles.input}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            data-testid="adjust-reason"
          />
        </label>
        <button
          type="button"
          className={styles.primary}
          onClick={() => void submitAdjustment()}
          data-testid="adjust-submit"
        >
          조정
        </button>
      </div>

      <h3 className={styles.subhead}>차감 정정</h3>
      <p className={styles.muted}>
        기존 차감 기록은 수정되지 않습니다. 취소 기록과 새 차감 기록이 추가됩니다.
      </p>
      <div className={styles.formGrid}>
        <label className={styles.filterField}>
          <span>차감 내역 ID</span>
          <input
            className={styles.input}
            value={entryId}
            onChange={(e) => setEntryId(e.target.value)}
            inputMode="numeric"
            data-testid="correct-entry"
          />
        </label>
        <label className={styles.filterField}>
          <span>새 차감액 (비우면 취소만)</span>
          <input
            className={styles.input}
            value={newAmount}
            onChange={(e) => setNewAmount(e.target.value)}
            inputMode="numeric"
            data-testid="correct-amount"
          />
        </label>
        <button
          type="button"
          className={styles.secondary}
          onClick={() => void submitCorrection()}
          data-testid="correct-submit"
        >
          정정
        </button>
      </div>
    </section>
  );
}
