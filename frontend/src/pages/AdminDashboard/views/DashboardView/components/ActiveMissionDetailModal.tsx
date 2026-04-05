import { useState } from 'react';
import styles from './DashboardModal.module.css';
import { getLocalToday } from '../../../../../shared/utils/dateUtils';
import AdminModal from '../../../components/AdminModal/AdminModal';
import PlayerTab from '../../../components/PlayerTab/PlayerTab';
import type { Mission, Player } from '../../../types/admin.types';
import type { CycleInfo } from '../../../hooks/useCycle';

interface Props {
  open:    boolean;
  onClose: () => void;
  missions: Mission[];
  players:  Player[];
  cycle:    Pick<CycleInfo, 'startDate' | 'endDate'>;
}

const STATUS_LABEL: Record<string, string> = {
  active: '진행중', completed: '완료', pending_approval: '승인대기',
  failed: '실패', rejected: '거절', proposed: '제안',
};
const STATUS_COLOR: Record<string, string> = {
  active: '#059669', completed: '#4338CA', pending_approval: '#D97706',
  failed: '#DC2626', rejected: '#DC2626', proposed: '#6366F1',
};

export default function ActiveMissionDetailModal({ open, onClose, missions, players, cycle }: Props) {
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
  const today = getLocalToday();

  const filtered = missions.filter((m) =>
    m.status === 'active' &&
    m.date >= cycle.startDate &&
    m.date >= today &&
    (selectedPlayer === null || m.player_id === selectedPlayer)
  );

  // date 기준 내림차순 그룹핑
  const grouped: Record<string, Mission[]> = {};
  filtered.forEach((m) => {
    if (!grouped[m.date]) grouped[m.date] = [];
    grouped[m.date].push(m);
  });
  const sortedDates = Object.keys(grouped).sort((a, b) => a.localeCompare(b));

  return (
    <AdminModal open={open} onClose={onClose} title="활성 미션 상세" width={520}>
      <PlayerTab players={players} selected={selectedPlayer} onSelect={setSelectedPlayer} />
      <div className={styles.listBody}>
        {sortedDates.length === 0 ? (
          <div className={styles.empty}>활성 미션이 없습니다</div>
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
                    <span
                      className={styles.statusBadge}
                      style={{ color: STATUS_COLOR[m.status] }}
                    >
                      {STATUS_LABEL[m.status] ?? m.status}
                    </span>
                  </div>
                );
              })}
            </div>
          ))
        )}
      </div>
    </AdminModal>
  );
}
