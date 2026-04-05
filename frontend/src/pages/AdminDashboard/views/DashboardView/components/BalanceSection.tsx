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
  cycleLabel: string;
}

export default function BalanceSection({ missions, players, cycleLabel }: BalanceSectionProps) {
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
      // 남은 포인트: 배정 총합 - 완료 총합 (failed 미션 제외)
      const pendingPoints = assignedPoints - donePoints;
      const rate = assignedPoints > 0 ? Math.round((donePoints / assignedPoints) * 100) : 0;
      return { id: p.id, name: p.name, assignedCount, assignedPoints, doneCount, donePoints, pendingPoints, rate };
    });
  }, [childPlayers, missions]);

  const maxAssigned = useMemo(() => Math.max(...balances.map(b => b.assignedPoints), 1), [balances]);
  const maxEarned   = useMemo(() => Math.max(...balances.map(b => b.donePoints), 1), [balances]);

  if (childPlayers.length === 0) return null;

  return (
    <div className={styles.section}>
      <div className={styles.sectionHeader}>
        <h3 className={styles.sectionTitle}>미션 밸런싱</h3>
        {cycleLabel && <span className={styles.sectionSub}>집계: {cycleLabel}</span>}
      </div>

      {/* 플레이어별 밸런싱 카드 */}
      <div className={styles.cardGrid}>
        {balances.map(b => (
          <div key={b.id} className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.avatar}>{b.name.slice(0, 1)}</div>
              <div className={styles.cardName}>{b.name}</div>
            </div>

            {/* ---- 미션 현황 ---- */}
            <div className={styles.rowLabel}>미션 현황</div>
            <div className={`${styles.statRow} ${styles.statRow2}`}>
              <div className={styles.statCell}>
                <div className={`${styles.statNum} ${styles.statPurple}`}>{b.assignedCount}</div>
                <div className={styles.statCellLabel}>배정</div>
              </div>
              <div className={styles.statCell}>
                <div className={`${styles.statNum} ${styles.statGreen}`}>{b.doneCount}</div>
                <div className={styles.statCellLabel}>완료</div>
              </div>
            </div>

            {/* 구분선 */}
            <div className={styles.separator} />

            {/* ---- 포인트 현황 ---- */}
            <div className={styles.rowLabel}>포인트 현황</div>
            <div className={`${styles.statRow} ${styles.statRow3}`}>
              <div className={styles.statCell}>
                <div className={`${styles.statNum} ${styles.statPurple}`} style={{ fontSize: '13px' }}>
                  {b.assignedPoints}P
                </div>
                <div className={styles.statCellLabel}>배정</div>
              </div>
              <div className={styles.statCell}>
                <div className={`${styles.statNum} ${styles.statGreen}`} style={{ fontSize: '13px' }}>
                  {b.donePoints}P
                </div>
                <div className={styles.statCellLabel}>획득</div>
              </div>
              <div className={styles.statCell}>
                <div className={`${styles.statNum} ${styles.statAmber}`} style={{ fontSize: '13px' }}>
                  {b.pendingPoints}P
                </div>
                <div className={styles.statCellLabel}>남은</div>
              </div>
            </div>

            <div className={styles.progressTrack}>
              <div className={styles.progressFill} style={{ width: `${b.rate}%` }} />
            </div>
            <div className={styles.rateLabel}>완료율 {b.rate}%</div>
          </div>
        ))}
      </div>

      {/* 포인트 밸런스 비교 — 세로 바 차트 */}
      <div className={styles.compareCard}>
        <div className={styles.compareHeader}>
          <div className={styles.compareTitle}>포인트 밸런스 비교</div>
          {cycleLabel && <div className={styles.compareSub}>집계: {cycleLabel}</div>}
        </div>

        <div className={styles.chartRow}>
          {/* 배정 포인트 그룹 */}
          <div className={styles.chartGroup}>
            <div className={styles.chartLabel}>배정 포인트</div>
            <div className={styles.verticalBars}>
              {balances.map(b => (
                <div key={`a-${b.id}`} className={styles.vBar}>
                  <div className={styles.vBarValue} style={{ color: '#3C3489' }}>
                    {b.assignedPoints > 0 ? `${b.assignedPoints}P` : '0'}
                  </div>
                  <div
                    className={`${styles.vBarBlock} ${styles.vBarPurple}`}
                    style={{ height: `${maxAssigned > 0 ? (b.assignedPoints / maxAssigned) * 100 : 0}%`, minHeight: '2px' }}
                  />
                  <div className={styles.vBarName}>{b.name}</div>
                </div>
              ))}
            </div>
          </div>

          {/* 구분선 */}
          <div className={styles.chartDivider} />

          {/* 획득 포인트 그룹 */}
          <div className={styles.chartGroup}>
            <div className={styles.chartLabel}>획득 포인트</div>
            <div className={styles.verticalBars}>
              {balances.map(b => (
                <div key={`e-${b.id}`} className={styles.vBar}>
                  <div className={styles.vBarValue} style={{ color: '#27500A' }}>
                    {b.donePoints > 0 ? `${b.donePoints}P` : '0'}
                  </div>
                  <div
                    className={`${styles.vBarBlock} ${styles.vBarGreen}`}
                    style={{ height: `${maxEarned > 0 ? (b.donePoints / maxEarned) * 100 : 0}%`, minHeight: '2px' }}
                  />
                  <div className={styles.vBarName}>{b.name}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
