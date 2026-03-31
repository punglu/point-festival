import { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import styles from './AdminLayout.module.css';
import Sidebar from './layout/Sidebar';
import AdminHeader from './layout/AdminHeader';
import MobileDrawer from './layout/MobileDrawer';
import { useAdminMenu } from './hooks/useAdminMenu';
import { useAdminFilter } from './hooks/useAdminFilter';

export default function AdminDashboard() {
  const { isMobileOpen, toggleMobile, closeMobile } = useAdminMenu();
  const { loadPlayers } = useAdminFilter();

  useEffect(() => {
    loadPlayers();
  }, [loadPlayers]);

  return (
    <div className={styles.adminLayout}>
      {/* 데스크톱: 사이드바 고정 */}
      <Sidebar className={styles.desktopSidebar} />

      {/* 모바일: Drawer 오버레이 */}
      <MobileDrawer isOpen={isMobileOpen} onClose={closeMobile} />

      <div className={styles.mainArea}>
        <AdminHeader onMenuToggle={toggleMobile} />
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
