import { useEffect, useState } from 'react';
import styles from '../UserDashboard.module.css';
import { dashboardApi, PlayerResponse, DailyPointResponse } from '../api/dashboardApi';

interface Props {
  currentPlayerId: number;
}

interface RankEntry {
  player: PlayerResponse;
  dailyPoint: DailyPointResponse | null;
}

export default function RankingView({ currentPlayerId }: Props) {
  const [entries, setEntries] = useState<RankEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10);
    const load = async () => {
      setLoading(true);
      try {
        const { data: players } = await dashboardApi.getPlayers();
        const results = await Promise.all(
          players
            .filter(p => p.role !== 'admin')
            .map(async player => {
              try {
                const res = await dashboardApi.getPointsRange(
                  player.id,
                  today.slice(0, 7) + '-01',
                  today,
                );
                const total = res.data.reduce((s, d) => s + d.balance, 0);
                return {
                  player,
                  dailyPoint: total > 0 ? { id: 0, player_id: player.id, date: today, earned: total, spent: 0, balance: total } : null,
                };
              } catch {
                return { player, dailyPoint: null };
              }
            }),
        );
        const sorted = results.sort((a, b) => (b.dailyPoint?.balance ?? 0) - (a.dailyPoint?.balance ?? 0));
        setEntries(sorted);
      } catch {
        // 조회 실패 시 빈 목록 유지
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <div className={styles.loading}>순위 불러오는 중...</div>;

  return (
    <div className={styles.progressSection}>
      <div className={styles.sectionHeader}>이번 달 포인트 순위</div>
      {entries.map((entry, i) => (
        <div
          key={entry.player.id}
          className={`${styles.progressCard} ${entry.player.id === currentPlayerId ? styles.progressCardHighlight : ''}`}
        >
          <span className={styles.progressRank}>{i + 1}</span>
          <span className={styles.progressName}>
            {entry.player.name}
            {entry.player.id === currentPlayerId && ' ⭐'}
          </span>
          <span className={styles.progressPoints}>{entry.dailyPoint?.balance ?? 0}P</span>
        </div>
      ))}
    </div>
  );
}
