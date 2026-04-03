import { useState } from 'react';
import styles from './MissionRanking.module.css';
import PlayerTab from '../../../components/PlayerTab/PlayerTab';
import CycleIndicator from '../../../components/CycleIndicator/CycleIndicator';
import type { MissionRankItem, Player } from '../../../types/admin.types';
import type { CycleInfo } from '../../../hooks/useCycle';

interface Props {
  ranking: MissionRankItem[];
  players: Player[];
  cycle: CycleInfo;
}

const RANK_STYLES: Record<number, { bg: string; color: string; label: string }> = {
  1: { bg: '#FFFBEB', color: '#B45309', label: '🥇' },
  2: { bg: '#F8FAFC', color: '#64748B', label: '🥈' },
  3: { bg: '#FFF7ED', color: '#C2673E', label: '🥉' },
};

export default function MissionRanking({ ranking, players, cycle }: Props) {
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);

  const selectedName = selectedPlayer
    ? players.find((p) => p.id === selectedPlayer)?.name ?? null
    : null;

  const filtered = selectedName
    ? ranking.filter((r) => (r.playerCounts[selectedName] ?? 0) > 0)
        .map((r) => ({
          ...r,
          totalCount: r.playerCounts[selectedName] ?? 0,
          playerCounts: { [selectedName]: r.playerCounts[selectedName] ?? 0 },
        }))
        .sort((a, b) => b.totalCount - a.totalCount)
    : ranking;

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <div className={styles.headerLeft}>
          <span className={styles.cardTitle}>미션 랭킹</span>
          <CycleIndicator cycle={cycle} />
        </div>
        <PlayerTab players={players} selected={selectedPlayer} onSelect={setSelectedPlayer} />
      </div>

      {filtered.length === 0 ? (
        <div className={styles.empty}>완료된 미션 없음</div>
      ) : (
        <div className={styles.grid}>
          {filtered.map((item, idx) => {
            const rank    = idx + 1;
            const rankStyle = RANK_STYLES[rank] ?? { bg: '#F8FAFC', color: '#94A3B8', label: `${rank}` };
            return (
              <div key={item.text} className={styles.rankCard} style={{ background: rankStyle.bg }}>
                <div className={styles.rankBadge} style={{ color: rankStyle.color }}>
                  {rankStyle.label}
                </div>
                <div className={styles.missionText}>{item.text}</div>
                <div className={styles.countRow}>
                  {Object.entries(item.playerCounts).map(([name, count]) => (
                    <span key={name} className={styles.playerCount}>
                      {name} {count}회
                    </span>
                  ))}
                  <span className={styles.total}>총 {item.totalCount}회</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
