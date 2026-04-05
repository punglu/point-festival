import { useMemo } from 'react';
import styles from './BalanceSection.module.css';
import type { Mission, Player } from '../../../types/admin.types';

interface PlayerBalance {
  id: number;
  name: string;
  assignedCount: number;
  assignedPoints: number;
  doneCount: number;
  donePoints: number;
  pendingPoints: number;
  rate: number;
}

interface BalanceSectionProps {
  missions: Mission[];
  players: Player[];
}

export default function BalanceSection({ missions, players }: BalanceSectionProps) {
  // 아이 플레이어만 (role='player'인 플레이어 — 아빠/엄마 제외)
  const childPlayers = useMemo(() => {
    return players.filter(p => p.role === 'player');
  }, [players]);

  const balances = useMemo<PlayerBalance[]>(() => {
    return childPlayers.map(p => {
      const myMissions = missions.filter(m => m.player_id === p.id);
      const assignedCount = myMissions.length;
      const assignedPoints = myMissions.reduce((s, m) => s + m.point, 0);
      const done = myMissions.filter(m => m.status === 'completed');
      const doneCount = done.length;
      const donePoints = done.reduce((s, m) => s + m.point, 0);
      const pending = myMissions.filter(m => m.status === 'active' || m.status === 'pending_approval');
      const pendingPoints = pending.reduce((s, m) => s + m.point, 0);
      const rate = assignedPoints > 0 ? Math.round((donePoints / assignedPoints) * 100) : 0;
      return { id: p.id, name: p.name, assignedCount, assignedPoints, doneCount, donePoints, pendingPoints, rate };
    });
  }, [childPlayers, missions]);

  const maxAssigned = useMemo(() => Math.max(...balances.map(b => b.assignedPoints), 1), [balances]);
  const maxEarned   = useMemo(() => Math.max(...balances.map(b => b.donePoints), 1), [balances]);

  if (childPlayers.length === 0) return null;

  return (
    <div className={styles.section}>
      <h3 className={styles.sectionTitle}>미션 밸런싱</h3>

      {/* 플레이어별 밸런싱 카드 */}
      <div className={styles.cardGrid}>
        {balances.map(b => (
          <div key={b.id} className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.avatar}>{b.name.slice(0, 1)}</div>
              <div className={styles.cardName}>{b.name}</div>
            </div>

            <div className={styles.statRow}>
              <div className={styles.stat}>
                <div className={styles.statNum}>{b.assignedCount}</div>
                <div className={styles.statLabel}>배정</div>
              </div>
              <div className={styles.stat}>
                <div className={`${styles.statNum} ${styles.statDone}`}>{b.doneCount}</div>
                <div className={styles.statLabel}>완료</div>
              </div>
              <div className={styles.stat}>
                <div className={`${styles.statNum} ${styles.statPending}`}>{b.pendingPoints}P</div>
                <div className={styles.statLabel}>예정</div>
              </div>
            </div>

            <div className={styles.progressTrack}>
              <div className={styles.progressFill} style={{ width: `${b.rate}%` }} />
            </div>
            <div className={styles.rateLabel}>완료율 {b.rate}%</div>
          </div>
        ))}
      </div>

      {/* 포인트 밸런스 비교 바 */}
      <div className={styles.compareCard}>
        <div className={styles.compareTitle}>포인트 밸런스 비교</div>

        <div className={styles.compareGroup}>
          <div className={styles.compareLabel}>배정 포인트 (이번 주기)</div>
          {balances.map(b => (
            <div key={b.id} className={styles.barRow}>
              <span className={styles.barName}>{b.name}</span>
              <div className={styles.barTrack}>
                <div
                  className={`${styles.barFill} ${styles.barAssigned}`}
                  style={{ width: `${(b.assignedPoints / maxAssigned) * 100}%` }}
                >
                  {b.assignedPoints > 0 && <span className={styles.barValue}>{b.assignedPoints}P</span>}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className={styles.compareGroup}>
          <div className={styles.compareLabel}>획득 포인트 (이번 주기)</div>
          {balances.map(b => (
            <div key={b.id} className={styles.barRow}>
              <span className={styles.barName}>{b.name}</span>
              <div className={styles.barTrack}>
                <div
                  className={`${styles.barFill} ${styles.barEarned}`}
                  style={{ width: `${(b.donePoints / maxEarned) * 100}%` }}
                >
                  {b.donePoints > 0 && <span className={styles.barValue}>{b.donePoints}P</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
