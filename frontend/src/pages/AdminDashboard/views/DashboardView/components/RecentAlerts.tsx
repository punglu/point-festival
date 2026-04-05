import { useNavigate } from 'react-router-dom';
import styles from './RecentAlerts.module.css';
import type { Notification } from '../../../types/admin.types';

function extractDate(body: string | null | undefined, createdAt: string): string {
  if (body) {
    const match = body.match(/(\d{4}-\d{2}-\d{2})/);
    if (match) return match[1];
  }
  const d = new Date(createdAt);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function inferRoute(n: Notification): string {
  if (n.type === 'approval_request' || n.type === 'proposal') {
    const date = extractDate(n.body, n.created_at);
    return `/admin/missions?date=${date}`;
  }
  const text = `${n.title} ${n.body ?? ''}`;
  if (/채팅|피드백|대화/.test(text))    return '/admin/chat';
  if (/포인트|차감/.test(text))          return '/admin/points';
  if (/플레이어/.test(text))             return '/admin/players';
  return '/admin';
}

interface Props {
  notifications: Notification[];
}

function timeAgo(isoStr: string): string {
  const diff = Date.now() - new Date(isoStr).getTime();
  const min  = Math.floor(diff / 60000);
  if (min < 1)  return '방금';
  if (min < 60) return `${min}분 전`;
  const hr = Math.floor(min / 60);
  if (hr < 24)  return `${hr}시간 전`;
  return `${Math.floor(hr / 24)}일 전`;
}

export default function RecentAlerts({ notifications }: Props) {
  const navigate = useNavigate();
  const recent   = notifications.slice(0, 3);

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <span className={styles.cardTitle}>최근 알림</span>
        <button className={styles.viewAll} onClick={() => navigate('/admin/notifications')}>
          전체 보기 →
        </button>
      </div>

      {recent.length === 0 ? (
        <div className={styles.empty}>알림 없음</div>
      ) : (
        <div className={styles.list}>
          {recent.map((n) => (
            <div
              key={n.id}
              className={`${styles.item} ${styles.itemClickable}`}
              onClick={() => navigate(inferRoute(n))}
            >
              <div className={n.is_read ? styles.dotRead : styles.dot} />
              <div className={styles.content}>
                <div className={styles.notifTitle}>{n.title}</div>
                {n.body && <div className={styles.notifBody}>{n.body}</div>}
              </div>
              <div className={styles.time}>{timeAgo(n.created_at)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
