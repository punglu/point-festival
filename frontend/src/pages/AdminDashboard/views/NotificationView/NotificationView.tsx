import { useState } from 'react';
import styles from './NotificationView.module.css';
import { useNotificationView } from './hooks/useNotificationView';
import NotificationFilter from './components/NotificationFilter';
import NotificationItem from './components/NotificationItem';
import { AdminNotificationSendScreen, adminNotificationSendFixture } from '../../../../screens/admin/AdminNotificationSend';

export default function NotificationView() {
  const { filtered, filter, setFilter, unreadCount, loading, markAsRead, markAllAsRead } = useNotificationView();
  const [showSend, setShowSend] = useState(false);

  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <h1 className={styles.title}>알림</h1>
        <div className={styles.headerActions}>
          <button className={styles.btnPrimary} onClick={() => setShowSend(true)}>알림 발송</button>
          {unreadCount > 0 && (
            <button className={styles.btnReadAll} onClick={markAllAsRead}>
              모두 읽음 처리
            </button>
          )}
        </div>
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

      {showSend && (
        <div className={styles.overlay} data-testid="admin-notification-send-overlay">
          {/* canonical 2t (관리자 알림 발송) — this view was previously an
              inbox only (read/filter/mark-read); no send/compose feature
              existed. No send API exists yet (TRUE_FUNCTIONAL_GAP, W7.5
              scope); canonical fixture used as an explicit pending adapter. */}
          <AdminNotificationSendScreen model={adminNotificationSendFixture} onCancel={() => setShowSend(false)} onSend={() => setShowSend(false)} />
        </div>
      )}
    </div>
  );
}
