import { useState, useEffect } from 'react';
import styles from './BatchCopyModal.module.css';
import { formatDate } from '../../../../../shared/utils/dateUtils';
import AdminModal from '../../../components/AdminModal/AdminModal';
import { adminApi } from '../../../api/adminApi';
import { useAdminToast } from '../../../hooks/useAdminToast';
import type { Mission, Player } from '../../../types/admin.types';

interface Props {
  open:    boolean;
  onClose: () => void;
  players: Player[];
  onDone:  () => void;
}

type SourceMode = 'today' | 'yesterday' | 'custom';
type TargetMode = 'tomorrow' | 'week_rest' | 'next_week' | 'custom';

function getDateStr(d: Date) { return formatDate(d); }

function getTargetDates(mode: TargetMode, customDate: string): string[] {
  const today = new Date();
  const dow   = today.getDay(); // 0=Sun,1=Mon,...,6=Sat
  const toDate = (d: Date) => getDateStr(d);

  if (mode === 'tomorrow') {
    const t = new Date(today); t.setDate(today.getDate() + 1);
    return [toDate(t)];
  }
  if (mode === 'week_rest') {
    // Tomorrow through this Sunday
    const dates: string[] = [];
    const daysLeft = dow === 0 ? 0 : 7 - dow; // days until Sun
    for (let i = 1; i <= daysLeft; i++) {
      const d = new Date(today); d.setDate(today.getDate() + i);
      dates.push(toDate(d));
    }
    return dates.length ? dates : [toDate(new Date(today.setDate(today.getDate() + 1)))];
  }
  if (mode === 'next_week') {
    // Next Mon → Sun
    const daysUntilNextMon = dow === 0 ? 1 : 8 - dow;
    return Array.from({ length: 7 }, (_, i) => {
      const d = new Date(); d.setDate(new Date().getDate() + daysUntilNextMon + i);
      return toDate(d);
    });
  }
  return customDate ? [customDate] : [];
}

export default function BatchCopyModal({ open, onClose, players, onDone }: Props) {
  const { showToast } = useAdminToast();
  const today     = getDateStr(new Date());
  const yesterday = (() => { const d = new Date(); d.setDate(d.getDate() - 1); return getDateStr(d); })();

  const [sourceMode,   setSourceMode]   = useState<SourceMode>('today');
  const [customSource, setCustomSource] = useState(today);
  const [targetMode,   setTargetMode]   = useState<TargetMode>('tomorrow');
  const [customTarget, setCustomTarget] = useState('');

  const [sourceMissions, setSourceMissions] = useState<Mission[]>([]);
  const [loadingSource,  setLoadingSource]  = useState(false);
  // selectedItems: { [missionId]: point }
  const [selected, setSelected] = useState<Record<number, number>>({});
  const [submitting, setSubmitting] = useState(false);

  const sourceDate = sourceMode === 'today' ? today : sourceMode === 'yesterday' ? yesterday : customSource;

  // Load source missions when source date changes
  useEffect(() => {
    if (!open) return;
    const ctrl = new AbortController();
    setLoadingSource(true);
    setSelected({});
    adminApi.getMissions({ date: sourceDate }, ctrl.signal)
      .then((r) => { if (!ctrl.signal.aborted) { setSourceMissions(r.data.filter((m) => m.status !== 'proposed')); } })
      .catch(() => {})
      .finally(() => { if (!ctrl.signal.aborted) setLoadingSource(false); });
    return () => ctrl.abort();
  }, [open, sourceDate]);

  const toggleMission = (m: Mission) => {
    setSelected((prev) => {
      if (m.id in prev) { const next = { ...prev }; delete next[m.id]; return next; }
      return { ...prev, [m.id]: m.point };
    });
  };

  const selectAll = () => {
    const next: Record<number, number> = {};
    sourceMissions.forEach((m) => { next[m.id] = m.point; });
    setSelected(next);
  };

  const setPoint = (id: number, point: number) => {
    setSelected((prev) => ({ ...prev, [id]: point }));
  };

  const selectedIds = Object.keys(selected).map(Number);
  const targetDates = getTargetDates(targetMode, customTarget);

  const handleSubmit = async () => {
    if (selectedIds.length === 0 || targetDates.length === 0) return;
    setSubmitting(true);
    try {
      // Group selected mission ids by player_id
      const byPlayer: Record<number, number[]> = {};
      sourceMissions
        .filter((m) => m.id in selected)
        .forEach((m) => {
          if (!byPlayer[m.player_id]) byPlayer[m.player_id] = [];
          byPlayer[m.player_id].push(m.id);
        });

      const calls = Object.entries(byPlayer).flatMap(([pid, mission_ids]) =>
        targetDates.map((toDate) =>
          adminApi.batchCopyMissions({
            player_id:   Number(pid),
            source_date: sourceDate,
            target_date: toDate,
            mission_ids,
          })
        )
      );
      await Promise.all(calls);
      showToast('success', `${selectedIds.length}개 미션 × ${targetDates.length}일 복제 완료!`);
      onDone();
      onClose();
    } catch {
      showToast('error', '복제 실패');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AdminModal open={open} onClose={onClose} title="과거 미션 가져오기" width={480}>
      {/* 원본 날짜 */}
      <div className={styles.formGroup}>
        <div className={styles.label}>복제 원본 날짜</div>
        <div className={styles.sourceRow}>
          <button className={sourceMode === 'today'     ? styles.sourceBtnActive : styles.sourceBtn} onClick={() => setSourceMode('today')}>오늘</button>
          <button className={sourceMode === 'yesterday' ? styles.sourceBtnActive : styles.sourceBtn} onClick={() => setSourceMode('yesterday')}>어제</button>
          <button className={sourceMode === 'custom'    ? styles.sourceBtnActive : styles.sourceBtn} onClick={() => setSourceMode('custom')}>날짜 선택</button>
        </div>
        {sourceMode === 'custom' && (
          <input type="date" className={`${styles.input} ${styles.inputMt}`} value={customSource} onChange={(e) => setCustomSource(e.target.value)} />
        )}
      </div>

      {/* 미션 선택 */}
      <div className={styles.formGroup}>
        <div className={styles.selectAllRow}>
          <div className={`${styles.label} ${styles.labelNoMb}`}>미션 선택</div>
          <div className={styles.selectAllRight}>
            <span className={styles.selectedCount}>{selectedIds.length}개 선택됨</span>
            <button className={styles.selectAllBtn} onClick={selectAll}>전체 선택</button>
          </div>
        </div>
        <div className={styles.missionList}>
          {loadingSource ? (
            <div className={styles.empty}>로딩 중...</div>
          ) : sourceMissions.length === 0 ? (
            <div className={styles.empty}>이 날짜에 미션이 없습니다</div>
          ) : (
            sourceMissions.map((m) => {
              const player = players.find((p) => p.id === m.player_id);
              const checked = m.id in selected;
              return (
                <div key={m.id} className={styles.missionRow}>
                  <input
                    type="checkbox"
                    className={styles.missionCheck}
                    checked={checked}
                    onChange={() => toggleMission(m)}
                  />
                  <span className={styles.missionText}>{m.text}</span>
                  {player && <span className={styles.playerBadge}>{player.name}</span>}
                  <input
                    type="number"
                    className={styles.pointInput}
                    value={checked ? selected[m.id] : m.point}
                    min={1}
                    disabled={!checked}
                    onChange={(e) => setPoint(m.id, Number(e.target.value))}
                  />
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* 복제 대상 날짜 */}
      <div className={styles.formGroup}>
        <div className={styles.label}>복제 대상</div>
        <div className={styles.targetGroup}>
          <button className={targetMode === 'tomorrow'  ? styles.targetBtnActive : styles.targetBtn} onClick={() => setTargetMode('tomorrow')}>내일</button>
          <button className={targetMode === 'week_rest' ? styles.targetBtnActive : styles.targetBtn} onClick={() => setTargetMode('week_rest')}>이번 주 남은 날</button>
          <button className={targetMode === 'next_week' ? styles.targetBtnActive : styles.targetBtn} onClick={() => setTargetMode('next_week')}>다음 주 전체</button>
          <button className={targetMode === 'custom'    ? styles.targetBtnActive : styles.targetBtn} onClick={() => setTargetMode('custom')}>날짜 선택</button>
        </div>
        {targetMode === 'custom' && (
          <input type="date" className={`${styles.input} ${styles.inputMt}`} value={customTarget} onChange={(e) => setCustomTarget(e.target.value)} />
        )}
        {targetDates.length > 1 && (
          <div className={styles.targetHint}>{targetDates.length}일에 복제됩니다</div>
        )}
      </div>

      <button
        className={styles.btnSubmit}
        onClick={handleSubmit}
        disabled={submitting || selectedIds.length === 0 || targetDates.length === 0}
      >
        {submitting ? '복제 중...' : `${selectedIds.length}개 미션 복제`}
      </button>
    </AdminModal>
  );
}
