import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './MobileHeader.module.css';
import { useAdminAuth } from '../../hooks/useAdminAuth';
import AdminBrandLogo from '../AdminBrandLogo/AdminBrandLogo';
import { useAuthStore } from '../../../../shared/stores/useAuthStore';
import { httpClient } from '../../../../shared/api/httpClient';

interface Props {
  onMenuClick:  () => void;
  onBellClick?: () => void;
  unreadCount?: number;
}

export default function MobileHeader({ onMenuClick, onBellClick, unreadCount = 0 }: Props) {
  const { adminDisplayName, adminPhoto, logout } = useAdminAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };
  const isLoggedIn = useAuthStore(s => s.isLoggedIn);
  const [chatUnread, setChatUnread] = useState(0);

  // 채팅 미읽음 폴링 — player/admin 모두 허용 (get_current_chat_user)
  useEffect(() => {
    if (!isLoggedIn) return;
    const fetchChatUnread = () => {
      httpClient.get<{ unread: number }>('/api/chat/unread')
        .then(res => setChatUnread(res.data.unread))
        .catch(() => {});
    };
    fetchChatUnread();
    const interval = setInterval(fetchChatUnread, 30000);
    return () => clearInterval(interval);
  }, [isLoggedIn]);

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
        <AdminBrandLogo />
      </div>

      <div className={styles.actions}>
        <button
          className={styles.homeBtn}
          onClick={() => navigate('/admin')}
          aria-label="홈으로 이동"
        >
          🏠
        </button>
        <button className={styles.headerChatBtn} aria-label="채팅" onClick={() => navigate('/admin/chat')}>
          💬
          {chatUnread > 0 && <span className={styles.headerChatBadge}>{chatUnread}</span>}
        </button>
        <button className={styles.iconBtn} aria-label="알림" onClick={onBellClick}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
            <path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          {unreadCount > 0 && <span className={styles.badgeDot} />}
        </button>

        <div className={styles.avatar}>
          {adminPhoto
            ? <img src={adminPhoto} alt={adminDisplayName ?? ''} className={styles.avatarImg} />
            : (adminDisplayName ?? 'A').charAt(0).toUpperCase()
          }
        </div>

        <button
          className={styles.mobileLogout}
          onClick={handleLogout}
          title="로그아웃"
        >
          <span className={styles.logoutText}>로그아웃</span>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4.5 10.5H2.5C2.23478 10.5 1.98043 10.3946 1.79289 10.2071C1.60536 10.0196 1.5 9.76522 1.5 9.5V2.5C1.5 2.23478 1.60536 1.98043 1.79289 1.79289C1.98043 1.60536 2.23478 1.5 2.5 1.5H4.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M8 8.5L10.5 6L8 3.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M10.5 6H4.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </header>
  );
}
