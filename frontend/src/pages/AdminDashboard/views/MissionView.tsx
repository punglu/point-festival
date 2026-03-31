import styles from './MissionView.module.css';
import { useAdminFilter } from '../hooks/useAdminFilter';
import MissionManager from '../components/MissionManager';
import CheerEditor from '../components/CheerEditor';

export default function MissionView() {
  const { selectedPlayerId, selectedDate } = useAdminFilter();

  return (
    <div className={styles.missionView}>
      <div className={styles.panel}>
        <MissionManager playerId={selectedPlayerId} selectedDate={selectedDate} />
      </div>
      <div className={styles.panel}>
        <CheerEditor selectedDate={selectedDate} />
      </div>
    </div>
  );
}
