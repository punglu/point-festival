import styles from './NotificationView.module.css';
import { useAdminFilter } from '../hooks/useAdminFilter';
import NotificationManager from '../components/NotificationManager';

export default function NotificationView() {
  const { selectedPlayerId } = useAdminFilter();

  return (
    <div className={styles.notificationView}>
      <div className={styles.panel}>
        <NotificationManager playerId={selectedPlayerId} />
      </div>
    </div>
  );
}
