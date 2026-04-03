import styles from './NotificationView.module.css';
import { useNotificationView } from './hooks/useNotificationView';
import NotificationFilter from './components/NotificationFilter';
import NotificationItem from './components/NotificationItem';

export default function NotificationView() {
  const { filtered, filter, setFilter, unreadCount, loading, markAsRead, markAllAsRead } = useNotificationView();

  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <h1 className={styles.title}>알림</h1>
        {unreadCount > 0 && (
          <button className={styles.btnReadAll} onClick={markAllAsRead}>
            모두 읽음 처리
          </button>
        )}
      </div>

      <NotificationFilter current={filter} unreadCount={unreadCount} onChange={setFilter} />

      {loading ? (
        <div className={styles.loading}>로딩 중...</div>
      ) : filtered.length === 0 ? (
        <div className={styles.empty}>알림이 없습니다</div>
      ) : (
        <div className={styles.list}>
          {filtered.map((n) => (
            <NotificationItem key={n.id} notification={n} onRead={markAsRead} />
          ))}
        </div>
      )}
    </div>
  );
}
