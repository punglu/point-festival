import { type ReactNode } from 'react';
import { Link, NavLink, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './MongleAppShell.module.css';

interface MongleAppShellProps {
  children: ReactNode;
}

const stateCopy = {
  loading: ['가족 정보를 확인하고 있어요', '계정과 가족 권한을 안전하게 불러오는 중입니다.'],
  mapping_required: ['계정 연결이 필요해요', '현재 로그인은 유지되지만 몽글 가족 기능을 사용하려면 검토된 계정 연결이 필요합니다.'],
  no_available_family: ['사용 가능한 가족이 없어요', '활성 가족 구성원으로 연결된 뒤 몽글 기능을 사용할 수 있습니다.'],
  family_selection_required: ['가족을 선택해주세요', '이 계정에 연결된 가족 중 하나를 선택하면 서비스와 권한을 불러옵니다.'],
  session_expired: ['세션이 만료됐어요', '다시 로그인하면 몽글 가족 정보를 안전하게 불러옵니다.'],
  forbidden: ['이 가족 정보를 열 수 없어요', '권한이 변경되었거나 접근이 허용되지 않은 상태입니다.'],
  backend_unavailable: ['몽글에 연결할 수 없어요', '잠시 후 다시 시도해주세요. 기존 마크포인트 화면은 별도 정책에 따라 유지됩니다.'],
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

export function MongleAppShell({ children }: MongleAppShellProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isAdmin, logout } = useAuthStore();
  const context = useFamilyContextStore((state) => state.context);
  const activeFamilyId = useFamilyContextStore((state) => state.activeFamilyId);
  const serviceStatus = useFamilyContextStore((state) => state.serviceStatus);
  const reset = useFamilyContextStore((state) => state.reset);
  const isLegacyDashboard = location.pathname === '/dashboard';
  const isAdminSurface = location.pathname.startsWith('/admin');
  // Wagle mobile conversation: ChatHeader가 화면의 주 헤더여야 하므로(Wave 6.0B §6.1),
  // 이 route+상태에서만, 그리고 모바일 폭에서만(CSS media query) 전역 상단 바를 숨긴다.
  // route/인증/FamilyContext 로직은 전혀 바꾸지 않는다 — 시각적 숨김뿐이다.
  // Room List(room 미선택)나 legacy/admin/다른 route에는 영향이 없다.
  // canonical path는 /wagle. 구 네임스페이스 alias는
  // MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001에서 제거됐다.
  const isWagleConversationMobile = location.pathname === '/wagle' && Boolean(searchParams.get('room'));
  const hasFamily = activeFamilyId !== null;
  const activeFamily = context?.families.find((family) => family.id === activeFamilyId);
  const hasPermission = (permission: string) => activeFamily?.permissions.includes(permission) ?? false;
  // Service code is `wagle` as of migration 0007, which renamed the whole
  // runtime identity. This reads real `/api/account-context` data, so comparing
  // against the historical code here silently reported every active Wagle
  // subscription as unavailable.
  const wagleState = serviceStatus('wagle');
  // MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001: navigation now points at the
  // Target screens. `/markpoint` replaces the legacy `/dashboard` entry, and
  // the two admin entries collapse into one `/markpoint/admin` whose panels are
  // gated per permission inside the screen — a mission manager and a point
  // admin see different halves of the same route.
  //
  // Visibility here is convenience only. Every screen re-checks with the
  // server, so a stale permission in this store can hide a link but can never
  // grant access.
  const markpointState = serviceStatus('markpoint');
  const canManageMissions = hasPermission('markpoint.missions.manage');
  const canAdjustPoints = hasPermission('markpoint.points.adjust');
  const navItems = [
    { to: '/markpoint', label: '마크포인트', visible: hasFamily && markpointState === 'active' },
    { to: '/wagle', label: '와글와글', visible: hasFamily },
    { to: '/family', label: '가족', visible: hasFamily && hasPermission('family.read') },
    {
      to: '/markpoint/admin',
      label: '마크포인트 관리',
      visible: hasFamily && (canManageMissions || canAdjustPoints),
    },
  ];

  const handleLogout = () => {
    reset();
    logout();
    navigate('/');
  };

  return (
    <div
      className={`${styles.shell} ${isWagleConversationMobile ? styles.wagleConversationMode : ''}`}
      data-testid="mongle-shell"
    >
      <header className={styles.header}>
        <Link className={styles.brand} to="/dashboard" aria-label="몽글 홈">몽글</Link>
        <FamilySwitcher />
        <div className={styles.accountArea}>
          <span>{context?.display_name ?? (isAdmin ? '관리자' : '사용자')}</span>
          <button onClick={handleLogout}>로그아웃</button>
        </div>
      </header>

      <div className={styles.body}>
        <nav className={styles.desktopNav} aria-label="몽글 서비스 탐색">
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
        <nav className={styles.mobileNav} aria-label="몽글 모바일 탐색">
          {/*
           * Wave 6.0B §8: 목업의 4-icon Bottom Dock 문법(elevated surface, 넉넉한
           * touch target, active=filled pill) 중 "icon+label"은 적용하지 못했다 —
           * 승인된 9종 outline icon(Home/Back/Bell/Settings/Edit/Delete/Attach/
           * Camera/Send) 중 마크포인트/와글와글/가족에 의미가 맞는 아이콘이 없고,
           * 새 아이콘을 만들지 않기로 했다(ASSET_GAP_BOTTOM_DOCK_ICONS, progress
           * log 참조). route 구성도 현재 실제 3개 목적지·기존 노출 동작(visible
           * 필터 없이 항상 3개)을 그대로 유지한다 — 목업의 "홈"/"나"는 대응 route가
           * 없어 새로 만들지 않는다(PM_DECISION_REQUIRED_BOTTOM_DOCK_ROUTE). 이번
           * 변경은 시각적 재스킨(icon+label 대신 label만, elevated pill)에 한정한다.
           */}
          <NavLink to="/dashboard" className={({ isActive }) => `${styles.dockItem} ${isActive ? styles.dockItemActive : ''}`}>
            <span className={styles.dockLabel}>마크포인트</span>
          </NavLink>
          <NavLink to="/wagle" className={({ isActive }) => `${styles.dockItem} ${isActive ? styles.dockItemActive : ''}`}>
            <span className={styles.dockLabel}>와글와글</span>
          </NavLink>
          <NavLink to="/family" className={({ isActive }) => `${styles.dockItem} ${isActive ? styles.dockItemActive : ''}`}>
            <span className={styles.dockLabel}>가족</span>
          </NavLink>
        </nav>
      )}
      {wagleState !== 'active' && location.pathname === '/wagle' && (
        <span className={styles.srOnly}>와글와글은 아직 사용할 수 없는 서비스입니다.</span>
      )}
    </div>
  );
}
