import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Sidebar from './components/Sidebar/Sidebar';
import MobileHeader from './components/MobileHeader/MobileHeader';
import MobileDrawer from './components/MobileDrawer/MobileDrawer';
import styles from './AdminLayout.module.css';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div className={styles.layout}>
      {/* 데스크탑 사이드바 */}
      <div className={styles.sidebarDesktop}>
        <Sidebar currentPath={location.pathname} />
      </div>

      {/* 모바일 헤더 */}
      <div className={styles.mobileHeader}>
        <MobileHeader
          onMenuClick={() => setDrawerOpen(true)}
          onBellClick={() => navigate('/admin/notifications')}
        />
      </div>

      {/* 모바일 Drawer */}
      <MobileDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        currentPath={location.pathname}
      />

      {/* 메인 콘텐츠 */}
      <main className={styles.main}>
        {children}
      </main>
    </div>
  );
}
