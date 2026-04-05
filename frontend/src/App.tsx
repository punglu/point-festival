import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/Auth';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import { useAuthStore } from './shared/stores/useAuthStore';
import ToastContainer from './shared/components/Toast/ToastContainer';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn } = useAuthStore();
  if (!isLoggedIn) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function AdminProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn, isAdmin } = useAuthStore();
  if (!isLoggedIn) return <Navigate to="/" replace />;
  if (!isAdmin) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <>
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
                <div data-domain="user">
                  <UserDashboard />
                </div>
              </ProtectedRoute>
            }
          />

          {/* "/admin/*" → Admin 계정만 접근 (내부 라우팅은 AdminDashboard/index.tsx) */}
          <Route
            path="/admin/*"
            element={
              <AdminProtectedRoute>
                <div data-domain="admin">
                  <AdminDashboard />
                </div>
              </AdminProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
      <ToastContainer />
    </>
  );
}
