import { useState } from 'react';
import styles from './DashboardModal.module.css';
import AdminModal from '../../../components/AdminModal/AdminModal';
import PlayerTab from '../../../components/PlayerTab/PlayerTab';
import type { Mission, Player } from '../../../types/admin.types';
import type { CycleInfo } from '../../../hooks/useCycle';

interface Props {
  open:    boolean;
  onClose: () => void;
  missions: Mission[];
  players:  Player[];
  cycle:    Pick<CycleInfo, 'startDate' | 'endDate' | 'label'>;
}

export default function CompletedMissionsModal({ open, onClose, missions, players, cycle }: Props) {
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);

  const completed = missions.filter((m) =>
    m.status === 'completed' &&
    m.date >= cycle.startDate &&
    m.date <= cycle.endDate &&
    (selectedPlayer === null || m.player_id === selectedPlayer)
  );

  const grouped: Record<string, Mission[]> = {};
  completed.forEach((m) => {
    if (!grouped[m.date]) grouped[m.date] = [];
    grouped[m.date].push(m);
  });
  const sortedDates = Object.keys(grouped).sort((a, b) => b.localeCompare(a));

  const totalPoints = completed.reduce((s, m) => s + m.point, 0);

  // 아이별 요약
  const playerSummary = players.map((p) => {
    const pm = completed.filter((m) => m.player_id === p.id);
    return { name: p.name, count: pm.length, points: pm.reduce((s, m) => s + m.point, 0) };
  }).filter((s) => s.count > 0);

  return (
    <AdminModal open={open} onClose={onClose} title="이번 주 완료 미션" subtitle={cycle.label} width={520}>
      <PlayerTab players={players} selected={selectedPlayer} onSelect={setSelectedPlayer} />
      <div className={styles.listBody}>
        {sortedDates.length === 0 ? (
          <div className={styles.empty}>완료된 미션이 없습니다</div>
        ) : (
          sortedDates.map((date) => (
            <div key={date}>
              <div className={styles.dateHeader}>{date}</div>
              {grouped[date].map((m) => {
                const player = players.find((p) => p.id === m.player_id);
                return (
                  <div key={m.id} className={styles.missionRow}>
                    <span className={styles.missionText}>{m.text}</span>
                    <span className={styles.playerBadge}>{player?.name ?? '?'}</span>
                    <span className={styles.pointBadge}>{m.point}pt</span>
                  </div>
                );
              })}
            </div>
          ))
        )}
      </div>
      {playerSummary.length > 0 && (
        <div className={styles.summaryBox}>
          {playerSummary.map((s) => (
            <div key={s.name} className={styles.summaryRow}>
              <span className={styles.summaryName}>{s.name}</span>
              <span className={styles.summaryVal}>{s.count}건 · {s.points}pt</span>
            </div>
          ))}
          <div className={styles.summaryTotal}>합계 {totalPoints}pt</div>
        </div>
      )}
    </AdminModal>
  );
}
