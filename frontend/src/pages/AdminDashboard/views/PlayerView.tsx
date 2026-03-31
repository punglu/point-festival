import styles from './PlayerView.module.css';
import { useAdminFilter } from '../hooks/useAdminFilter';
import PlayerManager from '../components/PlayerManager';
import FeedbackViewer from '../components/FeedbackViewer';
import type { PlayerItem } from '../api/adminApi';

export default function PlayerView() {
  const { players, selectedPlayerId, selectedDate, loadPlayers } = useAdminFilter();

  return (
    <div className={styles.playerView}>
      <div className={styles.panel}>
        <PlayerManager players={players as PlayerItem[]} onRefresh={loadPlayers} />
      </div>
      <div className={styles.panel}>
        <FeedbackViewer playerId={selectedPlayerId} selectedDate={selectedDate} />
      </div>
    </div>
  );
}
