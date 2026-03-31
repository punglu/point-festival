import { NavLink, useNavigate } from 'react-router-dom';
import styles from './Sidebar.module.css';
import { ADMIN_MENU_ITEMS } from '../constants';
import { useAuthStore } from '../../../shared/stores/useAuthStore';

interface Props {
  className?: string;
  onNavigate?: () => void;
}

export default function Sidebar({ className, onNavigate }: Props) {
  const navigate = useNavigate();
  const { adminDisplayName, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <aside className={`${styles.sidebar} ${className ?? ''}`}>
      <div className={styles.brand}>
        <div className={styles.brandTitle}>⛏️ Point Hub</div>
        <div className={styles.brandSub}>관리자 콘솔</div>
      </div>

      <nav className={styles.nav}>
        {ADMIN_MENU_ITEMS.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            end={item.path === '/admin'}
            className={({ isActive }) =>
              `${styles.navItem} ${isActive ? styles.navItemActive : ''}`
            }
            onClick={onNavigate}
          >
            <span className={styles.navIcon}>{item.icon}</span>
            <span className={styles.navLabel}>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className={styles.profile}>
        <div className={styles.profileAvatar}>
          {(adminDisplayName ?? 'A').charAt(0)}
        </div>
        <span className={styles.profileName}>{adminDisplayName ?? '관리자'}</span>
        <button className={styles.logoutBtn} onClick={handleLogout}>
          로그아웃
        </button>
      </div>
    </aside>
  );
}
