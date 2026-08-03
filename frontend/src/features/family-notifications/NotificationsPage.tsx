import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { NotificationListScreen, notificationListFixture } from '../../screens/family/NotificationList';
import type { NotificationItem } from '../../screens/family/NotificationList';
import { listNotifications, markAllNotificationsRead, markNotificationRead, type AccountNotification } from '../../shared/api/accountNotificationApi';
import styles from './NotificationsPage.module.css';

function relativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return '방금 전';
  if (minutes < 60) return `${minutes}분 전`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 전`;
  return new Date(iso).toLocaleDateString('ko-KR');
}

function toNotificationItem(n: AccountNotification): NotificationItem {
  return { icon: '●', title: n.title, text: n.body ?? '', time: relativeTime(n.created_at), unread: n.read_at === null };
}

/**
 * `/family/notifications` — canonical 1n (알림, W7.5 Phase D
 * SLICE-NOTIFICATION-LIST). List and "모두 읽음" are real.
 *
 * No producer route exists anywhere yet (mission approval, point change,
 * etc. do not create a notification row) — a real family sees a real empty
 * list, not the fixture's five invented items. The fixture's category
 * filters (포인트/일정/앨범) have no real category data behind them either
 * (every notification defaults to `category: "general"`, disclosed rather
 * than filtered against data that doesn't exist) — only '전체'/'새 알림'
 * filter against something real (`read_at`).
 */
export function NotificationsPage() {
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState(notificationListFixture.activeFilter);
  const [notifications, setNotifications] = useState<AccountNotification[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const reload = () => {
    listNotifications().then(setNotifications).catch(() => setLoadError('알림을 불러오지 못했어요.'));
  };

  useEffect(() => {
    const controller = new AbortController();
    setLoadError(null);
    listNotifications(controller.signal)
      .then(setNotifications)
      .catch(() => { if (!controller.signal.aborted) setLoadError('알림을 불러오지 못했어요.'); });
    return () => controller.abort();
  }, []);

  const handleSelect = async (item: NotificationItem) => {
    const real = (notifications ?? []).find((n) => n.title === item.title);
    if (!real || real.read_at !== null) return;
    try {
      await markNotificationRead(real.id);
      reload();
    } catch {
      setLoadError('알림을 읽음 처리하지 못했어요.');
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      reload();
    } catch {
      setLoadError('알림을 모두 읽음 처리하지 못했어요.');
    }
  };

  const realItems = (notifications ?? []).map(toNotificationItem);
  const visible = activeFilter === '새 알림' ? realItems.filter((n) => n.unread) : realItems;
  const model = notifications === null
    ? { ...notificationListFixture, notifications: [], footerNote: loadError ?? notificationListFixture.footerNote }
    : { ...notificationListFixture, unreadCount: realItems.filter((n) => n.unread).length, notifications: visible, activeFilter };

  return (
    <div className={styles.wrap}>
      <NotificationListScreen
        model={model}
        onBack={() => navigate('/family')}
        onMarkAllRead={() => void handleMarkAllRead()}
        onFilter={setActiveFilter}
        onSelectNotification={(item) => void handleSelect(item)}
      />
    </div>
  );
}
