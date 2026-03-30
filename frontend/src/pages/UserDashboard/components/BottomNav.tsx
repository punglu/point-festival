import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from '../UserDashboard.module.css';
import { useAuthStore } from '../../../shared/stores/useAuthStore';

interface Props {
  activeNav: 'home' | 'ranking';
  setActiveNav: (nav: 'home' | 'ranking') => void;
}

export default function BottomNav({ activeNav, setActiveNav }: Props) {
  const { isAdmin } = useAuthStore();
  const navigate = useNavigate();
  const longPressTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const onTouchStart = () => {
    if (!isAdmin) return;
    longPressTimer.current = setTimeout(() => {
      navigate('/admin');
    }, 3000);
  };

  const onTouchEnd = () => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }
  };

  return (
    <nav
      className={styles.bottomNav}
      onTouchStart={onTouchStart}
      onTouchEnd={onTouchEnd}
      onMouseLeave={onTouchEnd}
    >
      <button
        className={`${styles.navItem} ${activeNav === 'home' ? styles.navItemActive : ''}`}
        onClick={() => setActiveNav('home')}
      >
        <span className={styles.navIcon}>🏠</span>
        <span className={styles.navLabel}>홈</span>
      </button>
      <button
        className={`${styles.navItem} ${activeNav === 'ranking' ? styles.navItemActive : ''}`}
        onClick={() => setActiveNav('ranking')}
      >
        <span className={styles.navIcon}>🏆</span>
        <span className={styles.navLabel}>순위</span>
      </button>
    </nav>
  );
}
