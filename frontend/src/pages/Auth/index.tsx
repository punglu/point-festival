import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { Toast } from '../../shared/components/Toast';
import styles from './Auth.module.css';
import ProfileSelectorContainer from './components/ProfileSelectorContainer';
import PinInputView from './components/PinInputView';
import AdminLoginView from './components/AdminLoginView';

interface Player {
  id: number;
  name: string;
  photo?: string | null;
}

type Mode = 'select' | 'pin' | 'admin';

export default function AuthPage() {
  const { isLoggedIn, isAdmin, isAccountSession } = useAuthStore();
  const [mode, setMode] = useState<Mode>('select');
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'error' | 'success' } | null>(() => {
    // 401 인터셉터가 세션 만료 플래그를 남긴 경우 토스트 표시
    if (sessionStorage.getItem('mc_session_expired')) {
      sessionStorage.removeItem('mc_session_expired');
      return { message: '세션이 만료되었습니다. 다시 로그인해주세요.', type: 'error' };
    }
    return null;
  });

  if (isLoggedIn) {
    // DEFECT-001 (MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-
    // REMEDIATION-001): `/dashboard` is the legacy *player* dashboard --
    // real and correct for a legacy player session, but it 404s for an
    // Account-native session (no `player` object exists there). An
    // Account-native session's own real home is `/family`; `AdminProtected
    // Route` is still the single place that decides real Admin access for
    // either credential system, this only fixes where a *non*-admin (or
    // not-yet-resolved) session lands from here.
    if (isAccountSession) return <Navigate to="/family" replace />;
    return <Navigate to={isAdmin ? '/admin' : '/dashboard'} replace />;
  }

  const handlePlayerSelect = (player: Player) => {
    setSelectedPlayer(player);
    setMode('pin');
  };

  const handleBackToSelect = () => {
    setSelectedPlayer(null);
    setMode('select');
  };

  const handleLoginError = (msg: string) => {
    setToast({ message: msg, type: 'error' });
    setMode('select');
    setSelectedPlayer(null);
  };

  return (
    <div className={styles.authContainer}>
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {mode === 'select' && (
        <ProfileSelectorContainer
          onPlayerSelect={handlePlayerSelect}
          onAdminClick={() => setMode('admin')}
        />
      )}
      {mode === 'pin' && selectedPlayer && (
        <PinInputView
          player={selectedPlayer}
          onBack={handleBackToSelect}
          onLoginError={handleLoginError}
        />
      )}
      {mode === 'admin' && (
        <AdminLoginView onBack={handleBackToSelect} />
      )}
    </div>
  );
}
