import styles from './PendingMissionCard.module.css';
import type { Mission, Player } from '../../../types/admin.types';

interface Props {
  missions: Mission[];
  players: Player[];
  onViewAll?: () => void;
}

function timeAgo(isoStr: string): string {
  const diff = Date.now() - new Date(isoStr).getTime();
  const min  = Math.floor(diff / 60000);
  if (min < 1)  return '방금';
  if (min < 60) return `${min}분 전`;
  const hr = Math.floor(min / 60);
  if (hr < 24)  return `${hr}시간 전`;
  return `${Math.floor(hr / 24)}일 전`;
}

export default function PendingMissionCard({ missions, players, onViewAll }: Props) {
  const pending   = missions.filter((m) => m.status === 'pending_approval').slice(0, 4);

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <span className={styles.cardTitle}>승인 대기</span>
        {pending.length > 0 && (
          <span className={styles.countBadge}>{pending.length}</span>
        )}
        {/* canonical 1m (미션 승인 대기함) -- W7.4-ADMIN-SINGLE-SOURCE-001:
            previously navigated away to /admin/missions (a plain filtered
            grid, no dedicated actionable queue); now opens the real
            approval queue in place. */}
        <button className={styles.viewAll} onClick={onViewAll}>
          전체 보기 →
        </button>
      </div>

      {pending.length === 0 ? (
        <div className={styles.empty}>대기 중인 미션 없음 ✓</div>
      ) : (
        <div className={styles.list}>
          {pending.map((m) => {
            const player      = players.find((p) => p.id === m.player_id);
            const isProposed  = m.status === 'pending_approval' && !!m.proposed_by;
            return (
              <div key={m.id} className={styles.item} style={{ borderLeftColor: isProposed ? '#818CF8' : '#D97706' }}>
                <div className={styles.missionName}>{m.text}</div>
                <div className={styles.missionMeta}>
                  <span className={styles.player}>{player?.name ?? '?'}</span>
                  <span className={styles.dot}>·</span>
                  <span className={styles.point}>{m.point}pt</span>
                  <span className={styles.dot}>·</span>
                  <span className={styles.time}>{timeAgo(m.created_at)}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
