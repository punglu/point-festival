import styles from './NotificationItem.module.css';
import type { Notification } from '../../../types/admin.types';

const TYPE_STYLES: Record<string, { label: string; color: string; bg: string }> = {
  approval_request: { label: '승인 요청', color: '#D97706', bg: '#FEF3C7' },
  proposal:         { label: '미션 제안', color: '#4338CA', bg: '#EEF2FF' },
  level_up:         { label: '레벨 업!',  color: '#059669', bg: '#D1FAE5' },
  cycle_reset:      { label: '사이클',    color: '#0284C7', bg: '#E0F2FE' },
  system:           { label: '시스템',    color: '#6B7280', bg: '#F3F4F6' },
};

interface Props {
  notification: Notification;
  onRead:       (id: number) => void;
}

export default function NotificationItem({ notification: n, onRead }: Props) {
  const t = TYPE_STYLES[n.type] ?? TYPE_STYLES.system;
  const timeStr = new Date(n.created_at).toLocaleString('ko', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  return (
    <div
      className={n.is_read ? styles.item : styles.itemUnread}
      onClick={() => { if (!n.is_read) onRead(n.id); }}
    >
      <div className={n.is_read ? styles.dotRead : styles.dot} />
      <div className={styles.content}>
        <div className={styles.topRow}>
          <span
            className={styles.typeBadge}
            style={{ color: t.color, background: t.bg }}
          >
            {t.label}
          </span>
          <span className={styles.title}>{n.title}</span>
        </div>
        {n.body && <div className={styles.body}>{n.body}</div>}
        <div className={styles.meta}>
          <span className={styles.time}>{timeStr}</span>
        </div>
      </div>
    </div>
  );
}
