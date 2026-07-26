import { type ReactNode } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './NaranAppShell.module.css';

interface NaranAppShellProps {
  children: ReactNode;
}

const stateCopy = {
  loading: ['가족 정보를 확인하고 있어요', '계정과 가족 권한을 안전하게 불러오는 중입니다.'],
  mapping_required: ['계정 연결이 필요해요', '현재 로그인은 유지되지만 나란 가족 기능을 사용하려면 검토된 계정 연결이 필요합니다.'],
  no_available_family: ['사용 가능한 가족이 없어요', '활성 가족 구성원으로 연결된 뒤 나란 기능을 사용할 수 있습니다.'],
  family_selection_required: ['가족을 선택해주세요', '이 계정에 연결된 가족 중 하나를 선택하면 서비스와 권한을 불러옵니다.'],
  session_expired: ['세션이 만료됐어요', '다시 로그인하면 나란 가족 정보를 안전하게 불러옵니다.'],
  forbidden: ['이 가족 정보를 열 수 없어요', '권한이 변경되었거나 접근이 허용되지 않은 상태입니다.'],
  backend_unavailable: ['나란에 연결할 수 없어요', '잠시 후 다시 시도해주세요. 기존 마크포인트 화면은 별도 정책에 따라 유지됩니다.'],
} as const;

function FamilySwitcher() {
  const context = useFamilyContextStore((state) => state.context);
  const activeFamilyId = useFamilyContextStore((state) => state.activeFamilyId);
  const selectFamily = useFamilyContextStore((state) => state.selectFamily);

  if (!context || context.families.length === 0) return null;
  return (
    <label className={styles.familySwitcher}>
      <span>가족</span>
      <select
        aria-label="활성 가족 선택"
        value={activeFamilyId ?? ''}
        onChange={(event) => selectFamily(Number(event.target.value))}
      >
        {activeFamilyId === null && <option value="" disabled>가족 선택</option>}
        {context.families.map((family) => (
          <option key={family.id} value={family.id}>{family.name}</option>
        ))}
      </select>
    </label>
  );
}

function PlatformStateNotice() {
  const status = useFamilyContextStore((state) => state.status);
  const navigate = useNavigate();
  const reset = useFamilyContextStore((state) => state.reset);
  const logout = useAuthStore((state) => state.logout);
  const copy = stateCopy[status as keyof typeof stateCopy];
  if (!copy) return null;

  const sessionExpired = status === 'session_expired';
  return (
    <section className={styles.stateNotice} role={status === 'loading' ? 'status' : 'alert'} aria-live="polite">
      <div>
        <strong>{copy[0]}</strong>
        <p>{copy[1]}</p>
      </div>
      {sessionExpired && (
        <button onClick={() => { reset(); logout(); navigate('/'); }}>로그인으로 이동</button>
      )}
    </section>
  );
}

export function NaranAppShell({ children }: NaranAppShellProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAdmin, logout } = useAuthStore();
  const context = useFamilyContextStore((state) => state.context);
  const activeFamilyId = useFamilyContextStore((state) => state.activeFamilyId);
  const serviceStatus = useFamilyContextStore((state) => state.serviceStatus);
  const reset = useFamilyContextStore((state) => state.reset);
  const isLegacyDashboard = location.pathname === '/dashboard';
  const isAdminSurface = location.pathname.startsWith('/admin');
  const hasFamily = activeFamilyId !== null;
  const activeFamily = context?.families.find((family) => family.id === activeFamilyId);
  const hasPermission = (permission: string) => activeFamily?.permissions.includes(permission) ?? false;
  const doranState = serviceStatus('doran');
  const navItems = [
    { to: '/dashboard', label: '마크포인트', visible: true },
    { to: '/naran/doran', label: '도란', visible: hasFamily },
    { to: '/naran/family', label: '가족', visible: hasFamily && hasPermission('family.read') },
    { to: '/admin/missions', label: '미션 관리', visible: hasFamily && hasPermission('markpoint.missions.manage') },
    { to: '/admin/points', label: '포인트 관리', visible: hasFamily && hasPermission('markpoint.points.adjust') },
  ];

  const handleLogout = () => {
    reset();
    logout();
    navigate('/');
  };

  return (
    <div className={styles.shell} data-testid="naran-shell">
      <header className={styles.header}>
        <Link className={styles.brand} to="/dashboard" aria-label="나란 홈">나란</Link>
        <FamilySwitcher />
        <div className={styles.accountArea}>
          <span>{context?.display_name ?? (isAdmin ? '관리자' : '사용자')}</span>
          <button onClick={handleLogout}>로그아웃</button>
        </div>
      </header>

      <div className={styles.body}>
        <nav className={styles.desktopNav} aria-label="나란 서비스 탐색">
          {navItems.filter((item) => item.visible).map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => isActive ? styles.navActive : styles.navLink}>
              {item.label}
            </NavLink>
          ))}
          {isAdminSurface && <span className={styles.contextLabel}>관리자 화면</span>}
        </nav>

        <main className={`${styles.main} ${isLegacyDashboard ? styles.legacyMain : ''}`}>
          <PlatformStateNotice />
          {children}
        </main>
      </div>

      {!isLegacyDashboard && (
        <nav className={styles.mobileNav} aria-label="나란 모바일 탐색">
          <NavLink to="/dashboard">마크포인트</NavLink>
          <NavLink to="/naran/doran">도란</NavLink>
          <NavLink to="/naran/family">가족</NavLink>
        </nav>
      )}
      {doranState !== 'active' && location.pathname === '/naran/doran' && (
        <span className={styles.srOnly}>도란은 아직 사용할 수 없는 서비스입니다.</span>
      )}
    </div>
  );
}
