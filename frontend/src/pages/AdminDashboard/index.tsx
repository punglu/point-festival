import { Routes, Route, Navigate } from 'react-router-dom';
import AdminLayout from './AdminLayout';
import DashboardView from './views/DashboardView/DashboardView';
import MissionView from './views/MissionView/MissionView';
import PointView from './views/PointView/PointView';
import PlayerView from './views/PlayerView/PlayerView';
import NotificationView from './views/NotificationView/NotificationView';
import ConfigView from './views/ConfigView/ConfigView';
import FeedbackView from './views/FeedbackView/FeedbackView';

export default function AdminDashboard() {
  return (
    <AdminLayout>
      <Routes>
        <Route index                 element={<DashboardView />} />
        <Route path="missions"       element={<MissionView />} />
        <Route path="points"         element={<PointView />} />
        <Route path="players"        element={<PlayerView />} />
        <Route path="chat"           element={<FeedbackView />} />
        <Route path="notifications"  element={<NotificationView />} />
        <Route path="config"         element={<ConfigView />} />
        <Route path="*"              element={<Navigate to="/admin" replace />} />
      </Routes>
    </AdminLayout>
  );
}
