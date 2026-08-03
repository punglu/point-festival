import { useState } from 'react';
import styles from './NotificationView.module.css';
import { useNotificationView } from './hooks/useNotificationView';
import NotificationFilter from './components/NotificationFilter';
import NotificationItem from './components/NotificationItem';
import { AdminNotificationSendScreen, adminNotificationSendFixture } from '../../../../screens/admin/AdminNotificationSend';
import { adminApi } from '../../api/adminApi';

export default function NotificationView() {
  const { filtered, filter, setFilter, unreadCount, loading, markAsRead, markAllAsRead } = useNotificationView();
  const [showSend, setShowSend] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);

  const handleSend = async ({ subject, message }: { subject: string; message: string }) => {
    setIsSending(true);
    setSendError(null);
    try {
      // W7.5: recipients targeting stays "전체" — POST /api/admin/notifications
      // supports an optional player_id for a single recipient, but this
      // legacy admin surface has no per-family/per-member concept, so a
      // real "가족 구성원 선택" recipient picker is deferred (see the W7.5
      // Matrix note on 2t's admin/Account-native auth-model mismatch).
      await adminApi.createNotification({ title: subject, body: message });
      setShowSend(false);
    } catch {
      setSendError('알림을 발송하지 못했어요. 잠시 후 다시 시도해주세요.');
    } finally {
      setIsSending(false);
    }
  };

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
          {/* canonical 2t (관리자 알림 발송) — W7.5: wired to the real
              POST /api/admin/notifications (already existed; W7.4's "no send
              API exists yet" note was mistaken, corrected in the W7.5
              Matrix). */}
          <AdminNotificationSendScreen
            model={{ ...adminNotificationSendFixture, isSending, errorMessage: sendError }}
            onCancel={() => setShowSend(false)}
            onSend={handleSend}
          />
        </div>
      )}
    </div>
  );
}
