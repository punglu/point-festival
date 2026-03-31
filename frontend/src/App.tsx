import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/Auth';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import DashboardView from './pages/AdminDashboard/views/DashboardView';
import MissionView from './pages/AdminDashboard/views/MissionView';
import PointView from './pages/AdminDashboard/views/PointView';
import PlayerView from './pages/AdminDashboard/views/PlayerView';
import ConfigView from './pages/AdminDashboard/views/ConfigView';
import NotificationView from './pages/AdminDashboard/views/NotificationView';
import { useAuthStore } from './shared/stores/useAuthStore';

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
        {/* "/admin/*" → Admin 계정만 접근 (중첩 라우트) */}
        <Route
          path="/admin"
          element={
            <AdminProtectedRoute>
              <div data-domain="admin">
                <AdminDashboard />
              </div>
            </AdminProtectedRoute>
          }
        >
          <Route index element={<DashboardView />} />
          <Route path="mission" element={<MissionView />} />
          <Route path="point" element={<PointView />} />
          <Route path="player" element={<PlayerView />} />
          <Route path="config" element={<ConfigView />} />
          <Route path="notification" element={<NotificationView />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
