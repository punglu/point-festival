import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { NotificationListScreen, notificationListFixture } from '../../screens/family/NotificationList';
import styles from './NotificationsPage.module.css';

/**
 * `/family/notifications` — canonical 1n (알림, CHILD_OF 1b).
 * frontend/src/features/family-notifications/ was an empty scaffold with no
 * real entry point before this pass.
 */
export function NotificationsPage() {
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState(notificationListFixture.activeFilter);

  return (
    <div className={styles.wrap}>
      <NotificationListScreen
        model={{ ...notificationListFixture, activeFilter }}
        onBack={() => navigate('/family')}
        onMarkAllRead={() => undefined}
        onFilter={setActiveFilter}
        onSelectNotification={() => undefined}
      />
    </div>
  );
}
