import { useState, useEffect } from 'react';
import styles from '../AdminDashboard.module.css';
import { adminApi, NotificationItem } from '../api/adminApi';

interface Props {
  playerId: number | null;
}

export default function NotificationManager({ playerId }: Props) {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [loading, setLoading] = useState(false);

  const load = () => {
    const abortController = new AbortController();
    adminApi.getNotifications(abortController.signal)
      .then((res) => { if (!abortController.signal.aborted) setNotifications(res.data); })
      .catch(() => {});
    return () => abortController.abort();
  };

  useEffect(load, []);

  const handleCreate = async () => {
    if (!title.trim()) return;
    setLoading(true);
    try {
      await adminApi.createNotification({ type: 'admin', player_id: playerId ?? undefined, title: title.trim(), body: body.trim() || undefined });
      setTitle('');
      setBody('');
      load();
    } catch {
      alert('알림 생성 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (id: number) => {
    await adminApi.markNotificationRead(id);
    load();
  };

  return (
    <div className={styles.adminCard}>
      <div className={styles.adminCardTitle}>알림 관리</div>

      <div className={styles.formGroup}>
        <label className={styles.formLabel}>제목</label>
        <input className={styles.formInput} value={title} onChange={(e) => setTitle(e.target.value)} placeholder="알림 제목" />
      </div>
      <div className={styles.formGroup}>
        <label className={styles.formLabel}>내용 (선택)</label>
        <textarea className={styles.formTextarea} value={body} onChange={(e) => setBody(e.target.value)} placeholder="알림 내용" />
      </div>
      <button className={styles.btnPrimary} onClick={handleCreate} disabled={loading}>
        {loading ? '전송 중...' : '알림 추가'}
      </button>

      <div className={styles.adminCardTitle} style={{ fontSize: 14, marginTop: 20 }}>알림 목록</div>
      {notifications.length === 0 ? (
        <div className={styles.emptyMsg}>알림이 없습니다.</div>
      ) : (
        notifications.map((n) => (
          <div key={n.id} className={styles.listRow}>
            <div className={styles.listRowHeader}>
              <span className={styles.listRowTitle}>{n.title}</span>
              {!n.is_read && (
                <button className={`${styles.btnSecondary} ${styles.btnSm}`} onClick={() => handleMarkRead(n.id)}>읽음</button>
              )}
            </div>
            {n.body && <div className={styles.listRowBody}>{n.body}</div>}
            <div className={styles.listRowMeta}>{new Date(n.created_at).toLocaleString('ko-KR')}</div>
          </div>
        ))
      )}
    </div>
  );
}
