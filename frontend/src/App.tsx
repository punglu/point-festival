import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import AuthPage from './pages/Auth';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import { useAuthStore } from './shared/stores/useAuthStore';
import ToastContainer from './shared/components/Toast/ToastContainer';
import { FamilyContextLoader } from './shared/family/FamilyContextLoader';
import { MongleAppShell } from './platform/shell/MongleAppShell';
import { DoranLanding } from './platform/pages/DoranLanding';
import { FamilyLanding } from './platform/pages/FamilyLanding';
import { AccessBoundary } from './platform/access/AccessBoundary';
import pageStyles from './platform/pages/PlatformPages.module.css';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn } = useAuthStore();
  if (!isLoggedIn) return <Navigate to="/" replace />;
  return <>{children}</>;
}

// MONGLE-FE-ROUTE-ALIGNMENT-001 Wave 4: 등록되지 않은 경로 접근 시 빈 화면 대신
// 안내와 복귀 링크를 보여준다. 기존 route는 전혀 변경하지 않는다(최소 범위 복구).
function NotFoundPage() {
  return (
    <section className={pageStyles.page} role="alert">
      <h1>페이지를 찾을 수 없어요</h1>
      <p>주소가 바뀌었거나 존재하지 않는 페이지입니다.</p>
      <Link to="/">몽글로 돌아가기</Link>
    </section>
  );
}

function AdminProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn, isAdmin } = useAuthStore();
  if (!isLoggedIn || !isAdmin) return <Navigate to="/" replace />;
  return <>{children}</>;
}

// MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001: legacy `/naran/doran`·`/naran/family`
// compatibility alias. Preserves query string and hash, single-hop `replace`
// navigation (no history entry left behind, no Back-loop). The canonical
// route's own guard (ProtectedRoute) still applies after this redirect —
// this component itself carries no auth logic, matching §9 of the migration
// design ("공통 helper... 외부 side effect 없음").
function LegacyRouteRedirect({ to }: { to: string }) {
  const location = useLocation();
  return <Navigate to={`${to}${location.search}${location.hash}`} replace />;
}

export default function App() {
  return (
    <>
      <FamilyContextLoader>
      <BrowserRouter>
        <Routes>
          {/* "/" → 플레이어 선택 + PIN 인증 */}
          <Route
            path="/"
            element={
              <div data-domain="user">
                <AuthPage />
              </div>
            }
          />

          {/* "/dashboard" → 인증된 플레이어만 접근 */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <MongleAppShell><div data-domain="user"><UserDashboard /></div></MongleAppShell>
              </ProtectedRoute>
            }
          />

          {/* "/admin/*" → Admin 계정만 접근 (내부 라우팅은 AdminDashboard/index.tsx) */}
          <Route
            path="/admin/*"
            element={
              <AdminProtectedRoute>
                <MongleAppShell><div data-domain="admin"><AdminDashboard /></div></MongleAppShell>
              </AdminProtectedRoute>
            }
          />

          {/* MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001: canonical routes. */}
          <Route
            path="/wagle"
            element={<ProtectedRoute><MongleAppShell><DoranLanding /></MongleAppShell></ProtectedRoute>}
          />
          <Route
            path="/family"
            element={<ProtectedRoute><MongleAppShell><AccessBoundary permission="family.read"><FamilyLanding /></AccessBoundary></MongleAppShell></ProtectedRoute>}
          />

          {/* MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001: legacy compatibility aliases.
              KEEP UNTIL EXPLICIT CLEANUP GATE — do not remove without a separate,
              explicit PM-approved cleanup task. Registered explicitly (not left to
              the catch-all) so direct entry/bookmarks/deep-links to the old paths
              keep working, single-hop `replace`, query/hash preserved. */}
          <Route path="/naran/doran" element={<LegacyRouteRedirect to="/wagle" />} />
          <Route path="/naran/family" element={<LegacyRouteRedirect to="/family" />} />

          {/* MONGLE-FE-ROUTE-ALIGNMENT-001 Wave 4: 등록되지 않은 모든 경로의 최소 안전망.
              기존 route의 동작·우선순위는 변경하지 않는다 — React Router는 더 구체적인
              경로를 먼저 매칭하므로 이 catch-all은 위 어떤 route도 가리지 않는다. */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
      </FamilyContextLoader>
      <ToastContainer />
    </>
  );
}
