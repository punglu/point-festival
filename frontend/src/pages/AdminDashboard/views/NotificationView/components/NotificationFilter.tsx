import styles from './NotificationFilter.module.css';
import type { NotifFilter } from '../hooks/useNotificationView';

interface Tab { key: NotifFilter; label: string; }

const TABS: Tab[] = [
  { key: 'all',              label: '전체' },
  { key: 'unread',           label: '읽지 않음' },
  { key: 'approval_request', label: '승인 요청' },
  { key: 'proposal',         label: '미션 제안' },
];

interface Props {
  current:     NotifFilter;
  unreadCount: number;
  onChange:    (f: NotifFilter) => void;
}

export default function NotificationFilter({ current, unreadCount, onChange }: Props) {
  return (
    <div className={styles.filterBar}>
      {TABS.map((t) => (
        <button
          key={t.key}
          className={current === t.key ? styles.tabActive : styles.tab}
          onClick={() => onChange(t.key)}
        >
          {t.label}
          {t.key === 'unread' && unreadCount > 0 && (
            <span className={styles.badge}>{unreadCount}</span>
          )}
        </button>
      ))}
    </div>
  );
}
