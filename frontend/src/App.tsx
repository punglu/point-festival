import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import AuthPage from './pages/Auth';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import { useAuthStore } from './shared/stores/useAuthStore';
import ToastContainer from './shared/components/Toast/ToastContainer';
import { FamilyContextLoader } from './shared/family/FamilyContextLoader';
import { MongleAppShell } from './platform/shell/MongleAppShell';
import A1AccountLoginPage from './pages/A1AccountLogin';
import { PointFestivalPreview } from './pages/PointFestivalPreview';
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

          {/* Wave 6 recovery baseline: `/family`, `/markpoint*`, and `/wagle`
              remain detached from noncanonical UI. `/login` is the ordered A1
              presentation-only reconstruction; API/session code remains parked. */}
          <Route path="/login" element={<A1AccountLoginPage />} />

          {/* Wave 6 1c visual-only preview. This is intentionally not product
              navigation and has no API, session or dashboard connection. */}
          <Route path="/__wave6/1c" element={<PointFestivalPreview />} />

          {/* MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001:
              the `/naran/*` compatibility aliases were removed by explicit PM
              cutover. They are deliberately NOT redirected — keeping them
              registered, in any form, would keep a retired platform name alive
              in the router. Those paths now fall through to the catch-all
              below and render the not-found page. */}
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
