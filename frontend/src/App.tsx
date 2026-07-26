import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/Auth';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import { useAuthStore } from './shared/stores/useAuthStore';
import ToastContainer from './shared/components/Toast/ToastContainer';
import { FamilyContextLoader } from './shared/family/FamilyContextLoader';
import { NaranAppShell } from './platform/shell/NaranAppShell';
import { DoranLanding } from './platform/pages/DoranLanding';
import { FamilyLanding } from './platform/pages/FamilyLanding';
import { AccessBoundary } from './platform/access/AccessBoundary';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn } = useAuthStore();
  if (!isLoggedIn) return <Navigate to="/" replace />;
  return <>{children}</>;
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
                <NaranAppShell><div data-domain="user"><UserDashboard /></div></NaranAppShell>
              </ProtectedRoute>
            }
          />

          {/* "/admin/*" → Admin 계정만 접근 (내부 라우팅은 AdminDashboard/index.tsx) */}
          <Route
            path="/admin/*"
            element={
              <AdminProtectedRoute>
                <NaranAppShell><div data-domain="admin"><AdminDashboard /></div></NaranAppShell>
              </AdminProtectedRoute>
            }
          />

          <Route
            path="/naran/doran"
            element={<ProtectedRoute><NaranAppShell><DoranLanding /></NaranAppShell></ProtectedRoute>}
          />
          <Route
            path="/naran/family"
            element={<ProtectedRoute><NaranAppShell><AccessBoundary permission="family.read"><FamilyLanding /></AccessBoundary></NaranAppShell></ProtectedRoute>}
          />
        </Routes>
      </BrowserRouter>
      </FamilyContextLoader>
      <ToastContainer />
    </>
  );
}
