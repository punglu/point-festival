import styles from './WeeklyActivityChart.module.css';
import { getLocalToday, formatDate } from '../../../../../shared/utils/dateUtils';
import type { Mission, Player } from '../../../types/admin.types';
import type { CycleInfo } from '../../../hooks/useCycle';

interface Props {
  missions: Mission[];
  players: Player[];
  cycle: Pick<CycleInfo, 'startDate' | 'endDate'>;
}

const DAY_LABELS = ['월', '화', '수', '목', '금', '토', '일'];

// Distinct colors for up to 6 players
const PLAYER_COLORS = [
  '#4338CA', '#059669', '#D97706', '#DC2626', '#7C3AED', '#0891B2',
];

export default function WeeklyActivityChart({ missions, players, cycle }: Props) {
  const today = getLocalToday();

  // 주기 7일 날짜 배열
  const days: string[] = [];
  const start = new Date(cycle.startDate + 'T00:00:00');
  for (let i = 0; i < 7; i++) {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    days.push(formatDate(d));
  }

  const nonAdminPlayers = players.filter((p) => p.role !== 'admin');

  // [day][player] 완료 미션 수
  const matrix = days.map((day) =>
    nonAdminPlayers.map((p) =>
      missions.filter((m) => m.date === day && m.status === 'completed' && m.player_id === p.id).length
    )
  );

  const maxVal = Math.max(...matrix.flatMap((row) => row), 1);

  const totalCompleted = matrix.flatMap((r) => r).reduce((s, c) => s + c, 0);
  const totalMissions = missions.length;
  const completionPct = totalMissions > 0 ? Math.round((totalCompleted / totalMissions) * 100) : 0;

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <span className={styles.cardTitle}>이번 주 활동</span>
        <div className={styles.legend}>
          {nonAdminPlayers.map((p, i) => (
            <span key={p.id} className={styles.legendItem}>
              <span className={styles.legendDot} style={{ background: PLAYER_COLORS[i % PLAYER_COLORS.length] }} />
              {p.name}
            </span>
          ))}
        </div>
      </div>
      <div className={styles.chart}>
        {days.map((day, di) => {
          const isToday = day === today;
          return (
            <div key={day} className={styles.barCol}>
              <div className={styles.barWrap}>
                {nonAdminPlayers.map((p, pi) => {
                  const count = matrix[di][pi];
                  const heightPct = Math.round((count / maxVal) * 100);
                  return (
                    <div
                      key={p.id}
                      className={styles.bar}
                      style={{
                        height: `${Math.max(heightPct, count > 0 ? 8 : 0)}%`,
                        background: PLAYER_COLORS[pi % PLAYER_COLORS.length],
                        opacity: isToday ? 1 : 0.65,
                      }}
                      title={`${p.name}: ${count}건`}
                    />
                  );
                })}
              </div>
              <div className={isToday ? styles.dayLabelToday : styles.dayLabel}>
                {DAY_LABELS[di]}
              </div>
            </div>
          );
        })}
      </div>
      <div className={styles.footer}>
        <span className={styles.footerLabel}>완료율</span>
        <span className={styles.footerValue}>{completionPct}%</span>
        <span className={styles.footerSub}>({totalCompleted} / {totalMissions}건)</span>
      </div>
    </div>
  );
}
