import styles from './PlayerStatusCard.module.css';
import PlayerBadge from '../../../components/PlayerBadge/PlayerBadge';
import type { Player, Mission, DailyPoint } from '../../../types/admin.types';
import { LEVEL_THRESHOLDS } from '../../../constants/admin.constants';

interface Props {
  players: Player[];
  missions: Mission[];
  dailyPoints: DailyPoint[];
}

function calcLevel(points: number): number {
  let level = 1;
  for (let i = 0; i < LEVEL_THRESHOLDS.length; i++) {
    if (points >= LEVEL_THRESHOLDS[i]) level = i + 1;
  }
  return level;
}

function nextThreshold(points: number): number {
  for (const t of LEVEL_THRESHOLDS) {
    if (points < t) return t;
  }
  return LEVEL_THRESHOLDS[LEVEL_THRESHOLDS.length - 1];
}

export default function PlayerStatusCard({ players, missions, dailyPoints }: Props) {
  return (
    <div className={styles.card}>
      <div className={styles.cardTitle}>플레이어 현황</div>
      <div className={styles.list}>
        {players.map((p, idx) => {
          const totalEarned = dailyPoints
            .filter((dp) => dp.player_id === p.id)
            .reduce((s, dp) => s + dp.earned, 0);
          const activeMissions = missions.filter(
            (m) => m.player_id === p.id && m.status === 'active'
          ).length;
          const level = calcLevel(totalEarned);
          const next  = nextThreshold(totalEarned);
          const prevT = LEVEL_THRESHOLDS[level - 1] ?? 0;
          const pct   = next > prevT ? Math.round(((totalEarned - prevT) / (next - prevT)) * 100) : 100;

          return (
            <div key={p.id} className={styles.playerRow}>
              <PlayerBadge name={p.name} index={idx} size="md" photo={p.photo} />
              <div className={styles.playerInfo}>
                <div className={styles.nameRow}>
                  <span className={styles.name}>{p.name}</span>
                  <span className={styles.level}>Lv.{level}</span>
                  {activeMissions > 0 && (
                    <span className={styles.missionBadge}>{activeMissions}개 진행</span>
                  )}
                </div>
                <div className={styles.expRow}>
                  <div className={styles.expTrack}>
                    <div className={styles.expFill} style={{ width: `${pct}%` }} />
                  </div>
                  <span className={styles.expText}>{totalEarned}pt</span>
                </div>
              </div>
            </div>
          );
        })}
        {players.length === 0 && (
          <div className={styles.empty}>플레이어 없음</div>
        )}
      </div>
    </div>
  );
}
