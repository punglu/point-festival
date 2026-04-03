import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { Toast } from '../../shared/components/Toast';
import styles from './Auth.module.css';
import PlayerSelectView from './components/PlayerSelectView';
import PinInputView from './components/PinInputView';
import AdminLoginView from './components/AdminLoginView';

interface Player {
  id: number;
  name: string;
  photo?: string | null;
}

type Mode = 'select' | 'pin' | 'admin';

export default function AuthPage() {
  const { isLoggedIn, isAdmin } = useAuthStore();
  const [mode, setMode] = useState<Mode>('select');
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'error' | 'success' } | null>(null);

  if (isLoggedIn) {
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
        <PlayerSelectView
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
