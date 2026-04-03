import styles from './MobileHeader.module.css';
import { useAdminAuth } from '../../hooks/useAdminAuth';

interface Props {
  onMenuClick:  () => void;
  onBellClick?: () => void;
  unreadCount?: number;
}

export default function MobileHeader({ onMenuClick, onBellClick, unreadCount = 0 }: Props) {
  const { adminDisplayName } = useAdminAuth();

  return (
    <header className={styles.header}>
      <button className={styles.menuBtn} onClick={onMenuClick} aria-label="메뉴 열기">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      <div className={styles.brandArea}>
        <img src="/favicon-192x192.png" alt="포인트 잔치" className={styles.brandLogo} />
        <span className={styles.brandText}>포인트 잔치</span>
      </div>

      <div className={styles.actions}>
        <button className={styles.iconBtn} aria-label="알림" onClick={onBellClick}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
            <path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          {unreadCount > 0 && <span className={styles.badgeDot} />}
        </button>

        <div className={styles.avatar}>
          {(adminDisplayName ?? 'A').charAt(0).toUpperCase()}
        </div>
      </div>
    </header>
  );
}
