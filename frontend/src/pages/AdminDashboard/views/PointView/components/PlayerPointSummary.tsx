import styles from './PlayerPointSummary.module.css';
import type { Player, DailyPoint } from '../../../types/admin.types';

interface Props {
  players:     Player[];
  dailyPoints: DailyPoint[];
}

export default function PlayerPointSummary({ players, dailyPoints }: Props) {
  return (
    <div className={styles.section}>
      <div className={styles.sectionTitle}>포인트 현황</div>
      <div className={styles.grid}>
        {players.map((p) => {
          const pt = dailyPoints.find((d) => d.player_id === p.id);
          return (
            <div key={p.id} className={styles.card}>
              <div className={styles.playerName}>{p.name}</div>
              <div className={styles.stats}>
                <div className={styles.statRow}>
                  <span className={styles.statLabel}>획득</span>
                  <span className={styles.statEarned}>+{pt?.earned ?? 0}pt</span>
                </div>
                <div className={styles.statRow}>
                  <span className={styles.statLabel}>차감</span>
                  <span className={styles.statSpent}>-{pt?.spent ?? 0}pt</span>
                </div>
                <hr className={styles.divider} />
                <div className={styles.statRow}>
                  <span className={styles.statLabel}>잔액</span>
                  <span className={styles.statBalance}>{pt?.balance ?? 0}pt</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
