import { useState } from 'react';
import styles from '../AdminDashboard.module.css';
import { adminApi, MissionItem } from '../api/adminApi';

interface Props {
  playerId: number;
  sourceDate: string;
  targetDate: string;
  sourceMissions: MissionItem[];
  onClose: () => void;
  onCloned: () => void;
}

export default function MissionCloneModal({
  playerId,
  sourceDate,
  targetDate,
  sourceMissions,
  onClose,
  onCloned,
}: Props) {
  const [selected, setSelected] = useState<Set<number>>(new Set(sourceMissions.map((m) => m.id)));
  const [pointOverrides, setPointOverrides] = useState<Record<number, number>>({});
  const [loading, setLoading] = useState(false);

  const toggle = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleClone = async () => {
    setLoading(true);
    try {
      await adminApi.cloneMissions({
        source_player_id: playerId,
        source_date: sourceDate,
        target_date: targetDate,
        point_overrides: Object.keys(pointOverrides).length > 0 ? pointOverrides : null,
      });
      onCloned();
      onClose();
    } catch {
      alert('복제 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalBox} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalTitle}>미션 복제</div>

        <div className={styles.cloneInfoText}>
          원본: {sourceDate} → 대상: {targetDate}
        </div>

        {sourceMissions.map((m) => (
          <div key={m.id} className={styles.missionRow}>
            <input
              type="checkbox"
              checked={selected.has(m.id)}
              onChange={() => toggle(m.id)}
            />
            <span className={styles.missionText}>{m.text}</span>
            <input
              type="number"
              className={`${styles.formInput} ${styles.clonePointInput}`}
              value={pointOverrides[m.id] ?? m.point}
              onChange={(e) =>
                setPointOverrides((prev) => ({ ...prev, [m.id]: Number(e.target.value) }))
              }
              min={0}
            />
            <span className={styles.clonePointUnit}>P</span>
          </div>
        ))}

        <div className={styles.cloneSelectedCount}>
          선택된 미션: {selected.size}개
        </div>

        <button
          className={`${styles.btnPrimary} ${styles.cloneFullBtn}`}
          onClick={handleClone}
          disabled={loading || selected.size === 0}
        >
          {loading ? '복제 중...' : '복제 실행'}
        </button>
        <button className={styles.modalClose} onClick={onClose}>닫기</button>
      </div>
    </div>
  );
}
