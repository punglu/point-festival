import { NavLink, useNavigate } from 'react-router-dom';
import styles from './Sidebar.module.css';
import { ADMIN_MENU } from '../../constants/admin.constants';
import { useAdminAuth } from '../../hooks/useAdminAuth';
import AdminBrandLogo from '../AdminBrandLogo/AdminBrandLogo';

interface Props {
  currentPath: string;
  onNavigate?: () => void;
}

/* ── SVG 아이콘 (16×16 viewBox 24) ── */
function Icon({ name, className }: { name: string; className?: string }) {
  const paths: Record<string, string> = {
    dashboard:     'M3 3h7v7H3V3zm0 8h7v7H3v-7zm8-8h7v7h-7V3zm0 8h7v7h-7v-7z',
    missions:      'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
    points:        'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    players:       'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    notifications: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
    config:        'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z',
    chat:          'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
  };

  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={paths[name] ?? ''} />
    </svg>
  );
}

export default function Sidebar({ currentPath, onNavigate }: Props) {
  const { adminDisplayName, adminPhoto, logout } = useAdminAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const mainItems   = ADMIN_MENU.filter((m) => m.group === 'main');
  const manageItems = ADMIN_MENU.filter((m) => m.group === 'manage');

  const isActive = (path: string) =>
    path === '/admin' ? currentPath === '/admin' : currentPath.startsWith(path);

  return (
    <aside className={styles.sidebar}>
      {/* 브랜드 */}
      <div className={styles.brand} onClick={() => navigate('/admin')} style={{ cursor: 'pointer' }}>
        <AdminBrandLogo showSub />
      </div>

      {/* 내비게이션 */}
      <nav className={styles.nav}>
        <div className={styles.groupLabel}>메인</div>
        {mainItems.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            end={item.path === '/admin'}
            className={isActive(item.path) ? styles.menuItemActive : styles.menuItem}
            onClick={onNavigate}
          >
            <Icon name={item.icon} className={styles.menuIcon} />
            <span className={styles.menuLabel}>{item.label}</span>
            {item.badge != null && item.badge > 0 && (
              <span className={styles.badge}>{item.badge}</span>
            )}
          </NavLink>
        ))}

        <div className={styles.groupLabelMargin}>관리</div>
        {manageItems.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            className={isActive(item.path) ? styles.menuItemActive : styles.menuItem}
            onClick={onNavigate}
          >
            <Icon name={item.icon} className={styles.menuIcon} />
            <span className={styles.menuLabel}>{item.label}</span>
            {item.badge != null && item.badge > 0 && (
              <span className={styles.badge}>{item.badge}</span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* 프로필 */}
      <div className={styles.profile}>
        <div className={styles.profileAvatar}>
          {adminPhoto
            ? <img src={adminPhoto} alt={adminDisplayName ?? ''} className={styles.profileAvatarImg} />
            : (adminDisplayName ?? 'A').charAt(0).toUpperCase()
          }
        </div>
        <div className={styles.profileInfo}>
          <div className={styles.profileName}>{adminDisplayName ?? '관리자'}</div>
          <div className={styles.profileEmail}>admin@family</div>
        </div>
        <button className={styles.logoutBtn} onClick={handleLogout}>
          로그아웃
        </button>
      </div>
    </aside>
  );
}
