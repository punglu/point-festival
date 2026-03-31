import styles from './PointView.module.css';
import { useAdminFilter } from '../hooks/useAdminFilter';
import PointManager from '../components/PointManager';

export default function PointView() {
  const { selectedPlayerId, selectedDate } = useAdminFilter();

  return (
    <div className={styles.pointView}>
      <div className={styles.panel}>
        <PointManager playerId={selectedPlayerId} selectedDate={selectedDate} />
      </div>
    </div>
  );
}
