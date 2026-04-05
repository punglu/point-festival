import { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../../../api/adminApi';
import { useAdminToast } from '../../../hooks/useAdminToast';
import type { Notification } from '../../../types/admin.types';

export type NotifFilter = 'all' | 'unread' | 'approval_request' | 'proposal';

export function useNotificationView() {
  const { showToast } = useAdminToast();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter,        setFilter]        = useState<NotifFilter>('all');
  const [loading,       setLoading]       = useState(true);

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    try {
      const res = await adminApi.getNotifications(signal);
      if (!signal?.aborted) setNotifications(res.data);
    } catch (e) {
      if (!signal?.aborted && (e as { name?: string }).name !== 'CanceledError') {
        showToast('error', '알림 로드 실패');
      }
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    const ctrl = new AbortController();
    load(ctrl.signal);
    return () => ctrl.abort();
  }, [load]);

  // 승인요청/미션제안만 표시 (system·level_up·cycle_reset 제외)
  const actionable = notifications.filter((n) =>
    n.type === 'approval_request' || n.type === 'proposal'
  );

  const filtered = actionable.filter((n) => {
    switch (filter) {
      case 'unread':           return !n.is_read;
      case 'approval_request': return n.type === 'approval_request';
      case 'proposal':         return n.type === 'proposal';
      default:                 return true;
    }
  });

  const markAsRead = async (id: number) => {
    try {
      await adminApi.markAsRead(id);
      setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, is_read: true } : n));
    } catch { /* silent */ }
  };

  const markAllAsRead = async () => {
    try {
      await adminApi.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      showToast('success', '모두 읽음 처리됨');
    } catch { showToast('error', '처리 실패'); }
  };

  const unreadCount = actionable.filter((n) => !n.is_read).length;

  return {
    filtered, filter, setFilter, unreadCount, loading,
    markAsRead, markAllAsRead,
    reload: () => load(),
  };
}
