import { useNavigate } from 'react-router-dom';
import styles from './NotificationItem.module.css';
import type { Notification } from '../../../types/admin.types';

const TYPE_STYLES: Record<string, { label: string; color: string; bg: string }> = {
  approval_request: { label: '승인 요청', color: '#D97706', bg: '#FEF3C7' },
  proposal:         { label: '미션 제안', color: '#4338CA', bg: '#EEF2FF' },
};

/** body에서 날짜 추출: "2026-04-05 · +10pt" → "2026-04-05" */
function extractDate(body: string | null, createdAt: string): string {
  if (body) {
    const match = body.match(/(\d{4}-\d{2}-\d{2})/);
    if (match) return match[1];
  }
  // 구버전 body(날짜 없음) → created_at 로컬 날짜 폴백
  const d = new Date(createdAt);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

interface Props {
  notification: Notification;
  onRead:       (id: number) => void;
}

export default function NotificationItem({ notification: n, onRead }: Props) {
  const navigate = useNavigate();
  const t = TYPE_STYLES[n.type] ?? { label: n.type, color: '#6B7280', bg: '#F3F4F6' };
  const timeStr = new Date(n.created_at).toLocaleString('ko', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  const handleClick = () => {
    if (!n.is_read) onRead(n.id);
    if (n.type === 'approval_request' || n.type === 'proposal') {
      const date = extractDate(n.body, n.created_at);
      navigate(`/admin/missions?date=${date}`);
    }
  };

  return (
    <div
      className={`${n.is_read ? styles.item : styles.itemUnread} ${styles.clickable}`}
      onClick={handleClick}
    >
      <div className={n.is_read ? styles.dotRead : styles.dot} />
      <div className={styles.content}>
        <div className={styles.topRow}>
          <span className={styles.typeBadge} style={{ color: t.color, background: t.bg }}>
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
