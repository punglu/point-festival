/**
 * 마크포인트 사용자 화면 — the member's own points, level and missions.
 *
 * Every figure on this screen is read from the server and rendered as-is. The
 * screen never sums a ledger, never derives a balance and never advances a
 * mission's status: those are the Ledger's and the service's answers, and a
 * second computation here would be a second source of truth able to disagree
 * with the first.
 *
 * The distinction the layout is most careful about is **balance versus EXP**:
 *
 *   current_balance  — spendable, goes down when points are used
 *   lifetime_earned  — the level's input, never reduced by spending
 *
 * Showing one where the other belongs would make a child's level appear to
 * fall when they spend their points, which is exactly what the backend
 * contract is written to prevent.
 */
import { useCallback, useEffect, useState } from 'react';

import {
  getDeductionHistory,
  getLevel,
  getProjection,
  getWeekly,
  submitMission,
  updateMissionChecklist,
  MISSION_STATUS_LABEL,
  type MarkpointDeduction,
  type MarkpointLevel,
  type MarkpointProjection,
  type MarkpointWeekly,
  type MarkpointWeeklyDay,
  type MissionStatus,
} from '../../shared/api/markpointApi';

type WeeklyMission = MarkpointWeeklyDay['missions'][number];
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import { AccessBoundary } from '../access/AccessBoundary';
import { MissionDetailScreen, missionDetailFixture } from '../../screens/markpoint/MissionDetail';
import { MissionRejectScreen, missionRejectFixture } from '../../screens/markpoint/MissionReject';
import { LevelUpScreen } from '../../screens/markpoint/LevelUp';
import { ExchangeConfirmScreen } from '../../screens/markpoint/ExchangeConfirm';
import { RewardShopScreen, rewardShopFixture } from '../../screens/markpoint/RewardShop';
import { RewardExchangeScreen, rewardExchangeFixture } from '../../screens/markpoint/RewardExchange';
import { listRewards, redeemReward, type RewardCatalogItem } from '../../shared/api/rewardCatalogApi';
import styles from './MarkpointUser.module.css';

const REWARD_ICON = '🎁';

type LoadState = 'idle' | 'loading' | 'ready' | 'error' | 'forbidden';

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function MissionStatusBadge({ status }: { status: MissionStatus }) {
  return (
    <span className={`${styles.badge} ${styles[`badge_${status}`] ?? ''}`} data-status={status}>
      {MISSION_STATUS_LABEL[status] ?? status}
    </span>
  );
}

export function MarkpointUser() {
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const [state, setState] = useState<LoadState>('idle');
  const [projection, setProjection] = useState<MarkpointProjection | null>(null);
  const [weekly, setWeekly] = useState<MarkpointWeekly | null>(null);
  const [level, setLevel] = useState<MarkpointLevel | null>(null);
  const [deductions, setDeductions] = useState<MarkpointDeduction[]>([]);
  const [busyMissionId, setBusyMissionId] = useState<number | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [selectedMission, setSelectedMission] = useState<WeeklyMission | null>(null);
  const [showRejection, setShowRejection] = useState(false);
  const [showLevelUp, setShowLevelUp] = useState(false);
  const [rewardOverlay, setRewardOverlay] = useState<'none' | 'shop' | 'exchange'>('none');
  const [selectedReward, setSelectedReward] = useState<{ id: number; name: string; cost: number } | null>(null);
  const [rewards, setRewards] = useState<RewardCatalogItem[] | null>(null);
  const [redeemedRewardId, setRedeemedRewardId] = useState<number | null>(null);
  const [redeemError, setRedeemError] = useState<string | null>(null);

  const load = useCallback(
    async (familyId: number, signal?: AbortSignal) => {
      setState('loading');
      try {
        // Fetched together so the screen never renders a balance from one
        // moment beside a mission list from another.
        const [p, w, l, d] = await Promise.all([
          getProjection(familyId, signal),
          getWeekly(familyId, signal),
          getLevel(familyId, signal),
          getDeductionHistory(familyId, signal),
        ]);
        setProjection(p);
        setWeekly(w);
        setLevel(l);
        setDeductions(d);
        setState('ready');
      } catch (error: unknown) {
        if (signal?.aborted) return;
        const status = (error as { response?: { status?: number } }).response?.status;
        // 403 is a distinct outcome, not a generic failure: the member may have
        // Markpoint access withdrawn, or the family's subscription may be
        // inactive. Collapsing it into "try again later" would tell them to
        // retry something that will never succeed.
        setState(status === 403 ? 'forbidden' : 'error');
      }
    },
    [],
  );

  useEffect(() => {
    if (activeFamilyId === null) return undefined;
    const controller = new AbortController();
    void load(activeFamilyId, controller.signal);
    return () => controller.abort();
  }, [activeFamilyId, load]);

  const handleToggleChecklistItem = async (index: number) => {
    if (activeFamilyId === null || !selectedMission || !selectedMission.checklist) return;
    const updated = selectedMission.checklist.map((item, i) => (i === index ? { ...item, done: !item.done } : item));
    setSelectedMission({ ...selectedMission, checklist: updated });
    try {
      await updateMissionChecklist(activeFamilyId, selectedMission.id, updated);
      await load(activeFamilyId);
    } catch (error: unknown) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setActionError(detail ?? '체크리스트를 저장하지 못했어요. 잠시 후 다시 시도해주세요.');
      await load(activeFamilyId);
    }
  };

  useEffect(() => {
    if (activeFamilyId === null || rewardOverlay === 'none') return undefined;
    const controller = new AbortController();
    listRewards(activeFamilyId, controller.signal).then(setRewards).catch(() => setRewards([]));
    return () => controller.abort();
  }, [activeFamilyId, rewardOverlay]);

  const handleRedeem = async (rewardId: number) => {
    if (activeFamilyId === null) return;
    setRedeemError(null);
    try {
      await redeemReward(activeFamilyId, rewardId, `${rewardId}-${Date.now()}`);
      setRedeemedRewardId(rewardId);
      setSelectedReward(null);
      await load(activeFamilyId);
    } catch (error: unknown) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setRedeemError(detail ?? '포인트가 부족하거나 교환할 수 없는 보상이에요.');
      setSelectedReward(null);
    }
  };

  const handleSubmit = async (missionId: number) => {
    if (activeFamilyId === null) return;
    setBusyMissionId(missionId);
    setActionError(null);
    try {
      await submitMission(activeFamilyId, missionId);
      await load(activeFamilyId);
    } catch (error: unknown) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setActionError(detail ?? '미션을 제출하지 못했어요. 잠시 후 다시 시도해주세요.');
    } finally {
      setBusyMissionId(null);
    }
  };

  if (activeFamilyId === null) {
    return (
      <section className={styles.page}>
        <h1>가족을 선택해주세요</h1>
        <p className={styles.muted}>활성 가족을 선택하면 마크포인트를 이용할 수 있습니다.</p>
      </section>
    );
  }

  if (state === 'loading' || state === 'idle') {
    return (
      <section className={styles.page} aria-busy="true">
        <p className={styles.muted}>마크포인트를 불러오는 중…</p>
      </section>
    );
  }

  if (state === 'forbidden') {
    return (
      <section className={styles.page} role="alert">
        <h1>마크포인트를 이용할 수 없어요</h1>
        <p className={styles.muted}>
          가족의 마크포인트 서비스 상태나 이용 권한을 확인한 뒤 다시 시도해주세요.
        </p>
      </section>
    );
  }

  if (state === 'error') {
    return (
      <section className={styles.page} role="alert">
        <h1>마크포인트를 불러오지 못했어요</h1>
        <button type="button" className={styles.primary} onClick={() => void load(activeFamilyId)}>
          다시 시도
        </button>
      </section>
    );
  }

  const today = todayIso();

  return (
    <section className={styles.page} aria-labelledby="markpoint-title">
      <header className={styles.header}>
        <p className={styles.eyebrow}>몽글 · 마크포인트</p>
        <h1 id="markpoint-title">마크포인트</h1>
        <div className={styles.headerActions}>
          <button type="button" className={styles.secondary} onClick={() => setRewardOverlay('exchange')} data-testid="open-reward-exchange">
            보상 교환
          </button>
          <button type="button" className={styles.secondary} onClick={() => setRewardOverlay('shop')} data-testid="open-reward-shop">
            리워드샵
          </button>
        </div>
      </header>

      {/* Balance and EXP are deliberately separate cards. They are different
          numbers with different rules, and one card would invite reading a
          spend as a level loss. */}
      <div className={styles.cards}>
        <article className={styles.card} aria-labelledby="mp-balance">
          <h2 id="mp-balance" className={styles.cardTitle}>
            현재 포인트
          </h2>
          <p className={styles.bigNumber} data-testid="markpoint-balance">
            {projection?.current_balance ?? 0}
          </p>
          <dl className={styles.subStats}>
            <div>
              <dt>오늘 획득</dt>
              <dd data-testid="markpoint-today-earned">{projection?.today_earned ?? 0}</dd>
            </div>
            <div>
              <dt>오늘 차감</dt>
              <dd data-testid="markpoint-today-deducted">{projection?.today_deducted ?? 0}</dd>
            </div>
            <div>
              <dt>기간 획득</dt>
              <dd data-testid="markpoint-period-earned">{projection?.weekly_earned ?? 0}</dd>
            </div>
            <div>
              <dt>기간 차감</dt>
              <dd data-testid="markpoint-period-deducted">{projection?.weekly_deducted ?? 0}</dd>
            </div>
          </dl>
        </article>

        <article className={styles.card} aria-labelledby="mp-level">
          <h2 id="mp-level" className={styles.cardTitle}>
            레벨
            <button type="button" className={styles.levelUpTrigger} onClick={() => setShowLevelUp(true)} aria-label="레벨업 축하 보기" data-testid="open-level-up">
              🎉
            </button>
          </h2>
          <p className={styles.bigNumber} data-testid="markpoint-level">
            Lv.{level?.level ?? 1}
          </p>
          <p className={styles.levelTitle}>{level?.title ?? ''}</p>
          <div
            className={styles.progressTrack}
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={level?.progress_percent ?? 0}
            aria-label="다음 레벨까지 진행도"
          >
            <div className={styles.progressFill} style={{ width: `${level?.progress_percent ?? 0}%` }} />
          </div>
          {/* Labelled "누적" on purpose: this is lifetime_earned, and it is not
              the spendable balance above. */}
          <p className={styles.muted}>
            누적 획득 {projection?.lifetime_earned ?? 0} · 다음 {level?.next_threshold ?? 0}
          </p>
        </article>

        <article className={styles.card} aria-labelledby="mp-remaining">
          <h2 id="mp-remaining" className={styles.cardTitle}>
            남은 미션
          </h2>
          <p className={styles.bigNumber} data-testid="markpoint-remaining">
            {projection?.remaining_missions ?? 0}
          </p>
          <p className={styles.muted}>예상 {projection?.expected_points ?? 0}포인트</p>
        </article>
      </div>

      <section className={styles.block} aria-labelledby="mp-weekly">
        <h2 id="mp-weekly">
          이번 주기 미션
          <span className={styles.periodHint}>
            {weekly?.period_start} ~ {weekly?.period_end} · {weekly?.cycle_type}
          </span>
        </h2>

        {weekly && weekly.total_missions === 0 ? (
          <p className={styles.empty} data-testid="markpoint-weekly-empty">
            이번 주기에 배정된 미션이 없어요.
          </p>
        ) : (
          <ol className={styles.dayList} data-testid="markpoint-weekly-days">
            {weekly?.days.map((day) => (
              <li
                key={day.date}
                className={`${styles.day} ${day.date === today ? styles.dayToday : ''}`}
                data-date={day.date}
                data-today={day.date === today ? 'true' : undefined}
              >
                <div className={styles.dayHead}>
                  <span className={styles.dayDate}>{day.date.slice(5)}</span>
                  {day.date === today && <span className={styles.todayTag}>오늘</span>}
                </div>
                {/* An empty day is shown explicitly rather than omitted, so a
                    gap in the calendar is never ambiguous. */}
                {day.missions.length === 0 ? (
                  <p className={styles.dayEmpty}>미션 없음</p>
                ) : (
                  <ul className={styles.missionList}>
                    {day.missions.map((mission) => (
                      <li key={mission.id} className={styles.mission} data-mission-id={mission.id}>
                        <button
                          type="button"
                          className={styles.missionTitle}
                          onClick={() => setSelectedMission(mission)}
                          data-testid={`open-mission-detail-${mission.id}`}
                        >
                          {mission.title}
                        </button>
                        <span className={styles.missionReward}>+{mission.reward_amount}</span>
                        <MissionStatusBadge status={mission.status} />
                        {mission.status === 'active' && (
                          <button
                            type="button"
                            className={styles.secondary}
                            disabled={busyMissionId === mission.id}
                            onClick={() => void handleSubmit(mission.id)}
                            data-testid={`submit-mission-${mission.id}`}
                          >
                            {busyMissionId === mission.id ? '제출 중…' : '완료 요청'}
                          </button>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ol>
        )}
        {actionError && (
          <p className={styles.error} role="alert">
            {actionError}
          </p>
        )}
      </section>

      <section className={styles.block} aria-labelledby="mp-deductions">
        <h2 id="mp-deductions">차감 내역</h2>
        {deductions.length === 0 ? (
          <p className={styles.empty}>차감 내역이 없어요.</p>
        ) : (
          <ul className={styles.deductionList} data-testid="markpoint-deductions">
            {deductions.map((entry) => (
              <li key={entry.id} className={styles.deduction} data-entry-id={entry.id}>
                <span className={styles.deductionAmount}>{entry.amount}</span>
                <span className={styles.deductionReason}>{entry.reason ?? '사유 없음'}</span>
                <span className={styles.deductionDate}>{entry.occurred_at.slice(0, 10)}</span>
                {/* The original entry is never edited. A corrected one keeps its
                    original amount and gains this marker; the reversal and any
                    replacement appear as their own rows below it. */}
                {entry.corrected && <span className={styles.correctedTag}>정정됨</span>}
                {entry.reversal_of_entry_id !== null && (
                  <span className={styles.reversalTag}>#{entry.reversal_of_entry_id} 취소</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      {selectedMission && !showRejection && (
        <div className={styles.overlay} data-testid="markpoint-mission-detail-overlay">
          {/* canonical 1k (미션 상세) — title/reward/description/checklist are
              all real (own_weekly_detail, W7.5 Phase C). Photo evidence stays
              the static `photoNotice` copy: no file-storage abstraction exists
              anywhere in the backend (same POLICY_REQUIRED gate as Album/
              avatar upload, 2v/2z), so no upload control is wired. */}
          <MissionDetailScreen
            model={{
              title: selectedMission.title,
              description: selectedMission.description ?? '',
              reward: `+${selectedMission.reward_amount}P`,
              progressPercent: selectedMission.checklist && selectedMission.checklist.length > 0
                ? Math.round((selectedMission.checklist.filter((item) => item.done).length / selectedMission.checklist.length) * 100)
                : 0,
              completedCount: selectedMission.checklist?.filter((item) => item.done).length ?? 0,
              totalCount: selectedMission.checklist?.length ?? 0,
              checklist: selectedMission.checklist ?? [],
              photoNotice: missionDetailFixture.photoNotice,
              submitNotice: missionDetailFixture.submitNotice,
            }}
            onBack={() => setSelectedMission(null)}
            onToggleItem={(index) => void handleToggleChecklistItem(index)}
            onSubmit={
              selectedMission.status === 'rejected'
                ? () => setShowRejection(true)
                : () => { void handleSubmit(selectedMission.id); setSelectedMission(null); }
            }
          />
        </div>
      )}

      {selectedMission && showRejection && (
        <div className={styles.overlay} data-testid="markpoint-mission-reject-overlay">
          {/* canonical 1s (미션 반려) — title/summary/reviewer/reason are all
              real (own_weekly_detail's rejection_reason + reviewer_display_name,
              W7.5 Phase C). missionIcon stays static UI decoration, not data. */}
          <MissionRejectScreen
            model={{
              missionIcon: missionRejectFixture.missionIcon,
              missionTitle: selectedMission.title,
              missionSummary: `+${selectedMission.reward_amount}P`,
              reviewerName: selectedMission.reviewer_display_name ?? '보호자',
              reason: selectedMission.rejection_reason ?? '반려 사유가 기록되지 않았습니다.',
            }}
            onBack={() => setShowRejection(false)}
            onRetry={() => { setShowRejection(false); setSelectedMission(null); }}
          />
        </div>
      )}

      {showLevelUp && (
        <div className={styles.overlay} data-testid="markpoint-level-up-overlay">
          {/* canonical 2c (레벨업 축하) — manually triggered here for
              structural verification; a real product trigger would be an
              automatic event on level-up, which requires backend push
              support that does not exist yet (W7.5 scope). level/levelTitle
              are real (GET /api/me/markpoint/level). `bonusPoints: 0` is a
              disclosed absence, not a placeholder awaiting a field: no
              level-up bonus mechanic exists anywhere in the Ledger/mission
              pipeline (grep-confirmed, W7.5 Phase C) -- awarding one would be
              a real economy-affecting business-rule decision (amount, when
              triggered, every level vs. milestones only), not a response
              field to add. Reclassified accordingly in the Matrix; not
              treated as PARTIAL_WIRING_PENDING. */}
          <LevelUpScreen
            model={{
              playerInitial: (level?.title ?? '나').charAt(0),
              playerName: level?.title ?? '',
              level: level?.level ?? 1,
              levelTitle: level?.title ?? '',
              bonusPoints: 0,
            }}
            onConfirm={() => setShowLevelUp(false)}
          />
        </div>
      )}

      {rewardOverlay === 'shop' && (
        <div className={styles.overlay} data-testid="markpoint-reward-shop-overlay">
          {/* canonical 2j (리워드샵) — rewards/cost/availability are real
              (W7.5 Phase D SLICE-REWARD-CATALOG); balance is real (W7.4). */}
          <RewardShopScreen
            model={{
              ...rewardShopFixture,
              balance: projection?.current_balance ?? rewardShopFixture.balance,
              rewards: rewards === null
                ? rewardShopFixture.rewards
                : rewards.map((r) => ({ name: r.name, icon: REWARD_ICON, cost: r.cost, available: r.is_available })),
            }}
            onSelectReward={(reward) => {
              const real = (rewards ?? []).find((r) => r.name === reward.name);
              if (real) setSelectedReward({ id: real.id, name: real.name, cost: real.cost });
            }}
          />
          <button type="button" className={styles.overlayClose} onClick={() => setRewardOverlay('none')} aria-label="닫기">✕ 닫기</button>
        </div>
      )}

      {rewardOverlay === 'exchange' && (
        <div className={styles.overlay} data-testid="markpoint-reward-exchange-overlay">
          {/* canonical 1l (보상 교환) — same real catalog as 2j. */}
          <RewardExchangeScreen
            model={{
              ...rewardExchangeFixture,
              balance: projection?.current_balance ?? rewardExchangeFixture.balance,
              rewards: rewards === null
                ? rewardExchangeFixture.rewards
                : rewards.map((r) => ({ name: r.name, meta: '', action: `${r.cost}P 교환`, icon: REWARD_ICON, unavailable: !r.is_available })),
            }}
            onSelectReward={(reward) => {
              const real = (rewards ?? []).find((r) => r.name === reward.name);
              if (real) setSelectedReward({ id: real.id, name: real.name, cost: real.cost });
            }}
          />
        </div>
      )}

      {selectedReward && (
        <div className={styles.overlay} data-testid="markpoint-exchange-confirm-overlay">
          {/* canonical 2h (교환 확인) — reached by selecting a reward in
              either 리워드샵 (2j) or 보상 교환 (1l). onConfirm calls the real
              redemption endpoint (self-service Ledger debit); a failure
              (insufficient balance, no longer available) surfaces via
              redeemError rather than silently closing. */}
          <ExchangeConfirmScreen
            model={{
              icon: REWARD_ICON,
              rewardName: selectedReward.name,
              note: '',
              currentBalance: projection?.current_balance ?? 0,
              balanceAfter: Math.max(0, (projection?.current_balance ?? 0) - selectedReward.cost),
              cost: selectedReward.cost,
            }}
            onCancel={() => setSelectedReward(null)}
            onConfirm={() => { void handleRedeem(selectedReward.id); }}
          />
        </div>
      )}
      {redeemedRewardId !== null && !selectedReward && (
        <div className={styles.overlay} data-testid="markpoint-reward-redeemed-toast" role="status">
          <p>교환이 완료됐어요!</p>
          <button type="button" onClick={() => { setRedeemedRewardId(null); setRewardOverlay('none'); }}>확인</button>
        </div>
      )}
      {redeemError && (
        <p className={styles.error} role="alert">{redeemError}</p>
      )}
    </section>
  );
}

/** Route entry point. `markpoint.own.read` is the member-level permission;
 *  the boundary is server-confirmed on every request the screen makes. */
export function MarkpointUserPage() {
  return (
    <AccessBoundary permission="markpoint.own.read">
      <MarkpointUser />
    </AccessBoundary>
  );
}
