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

export default function PointHistoryModal({ open, onClose, missions, players, cycle }: Props) {
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);

  const history = missions
    .filter((m) =>
      m.status === 'completed' &&
      m.date >= cycle.startDate &&
      m.date <= cycle.endDate &&
      (selectedPlayer === null || m.player_id === selectedPlayer)
    )
    .sort((a, b) => b.date.localeCompare(a.date));

  const grouped: Record<string, Mission[]> = {};
  history.forEach((m) => {
    if (!grouped[m.date]) grouped[m.date] = [];
    grouped[m.date].push(m);
  });
  const sortedDates = Object.keys(grouped).sort((a, b) => b.localeCompare(a));

  const total = history.reduce((s, m) => s + m.point, 0);

  return (
    <AdminModal open={open} onClose={onClose} title="포인트 발행 이력" subtitle={cycle.label} width={520}>
      <PlayerTab players={players} selected={selectedPlayer} onSelect={setSelectedPlayer} />
      <div className={styles.listBody}>
        {sortedDates.length === 0 ? (
          <div className={styles.empty}>포인트 발행 이력이 없습니다</div>
        ) : (
          sortedDates.map((date) => {
            const dayTotal = grouped[date].reduce((s, m) => s + m.point, 0);
            return (
              <div key={date}>
                <div className={styles.dateHeader}>
                  {date}
                  <span className={styles.dateSubtotal}>{dayTotal}pt</span>
                </div>
                {grouped[date].map((m) => {
                  const player = players.find((p) => p.id === m.player_id);
                  return (
                    <div key={m.id} className={styles.missionRow}>
                      <span className={styles.missionText}>{m.text}</span>
                      <span className={styles.playerBadge}>{player?.name ?? '?'}</span>
                      <span className={styles.pointBadge}>+{m.point}pt</span>
                    </div>
                  );
                })}
              </div>
            );
          })
        )}
      </div>
      {history.length > 0 && (
        <div className={styles.summaryBox}>
          <div className={styles.summaryTotal}>총 발행 {total}pt</div>
        </div>
      )}
    </AdminModal>
  );
}
