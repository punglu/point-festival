import PlayerSelector from './components/PlayerSelector';
import LoginOverlay from './components/LoginOverlay';
import { useAuth } from './hooks/useAuth';

export default function AuthPage() {
  const {
    players, selectedPlayer, showOverlay,
    error, lockedMessage,
    selectPlayer, submitLogin, cancelLogin,
  } = useAuth();

  return (
    <>
      <PlayerSelector players={players} onSelect={selectPlayer} />

      {showOverlay && selectedPlayer && (
        <LoginOverlay
          playerName={selectedPlayer.name}
          lastLogin={selectedPlayer.lastLogin}
          onSubmit={submitLogin}
          onCancel={cancelLogin}
          error={error}
          lockedMessage={lockedMessage}
        />
      )}
    </>
  );
}
