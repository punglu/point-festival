import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/authApi';
import { useAuthStore } from '../../../shared/stores/useAuthStore';

interface PlayerInfo {
  id: number;
  name: string;
  isLocked: boolean;
  lastLogin: string | null;
}

export function useAuth() {
  const navigate = useNavigate();
  const { setLogin } = useAuthStore();

  const [players, setPlayers] = useState<PlayerInfo[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerInfo | null>(null);
  const [showOverlay, setShowOverlay] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lockedMessage, setLockedMessage] = useState<string | null>(null);

  useEffect(() => {
    authApi.getPlayers()
      .then((list) =>
        setPlayers(
          list
            .filter((p) => p.role === 'player')
            .map((p) => ({
              id: p.id,
              name: p.name,
              isLocked: p.is_locked,
              lastLogin: p.last_login
                ? new Date(p.last_login).toLocaleString('ko-KR')
                : null,
            })),
        ),
      )
      .catch(() => setPlayers([]));
  }, []);

  const selectPlayer = useCallback(
    (playerId: number) => {
      const player = players.find((p) => p.id === playerId);
      if (!player) return;
      if (player.isLocked) {
        alert('🔒 잠금 상태입니다. 잠시 후 다시 시도해주세요.');
        return;
      }
      setSelectedPlayer(player);
      setShowOverlay(true);
      setError(null);
      setLockedMessage(null);
    },
    [players],
  );

  const submitLogin = useCallback(
    async (pin: string, rememberMe: boolean) => {
      if (!selectedPlayer) return;
      setError(null);

      try {
        const res = await authApi.login({
          player_id: selectedPlayer.id,
          pin,
          remember_me: rememberMe,
        });

        setLogin(
          res.access_token,
          { id: res.player_id, name: res.player_name, role: res.player_role },
          res.is_admin ?? false,
        );

        if (rememberMe) {
          localStorage.setItem('loggedInPlayer', String(res.player_id));
          localStorage.setItem('rememberMe', 'true');
        }

        setShowOverlay(false);
        navigate(res.is_admin ? '/admin' : '/dashboard');
      } catch (err: unknown) {
        const httpErr = err as { response?: { status?: number; data?: { detail?: string } } };
        const httpStatus = httpErr.response?.status;
        const detail = httpErr.response?.data?.detail || '로그인 실패';

        if (httpStatus === 423) {
          setLockedMessage(detail);
          setTimeout(() => setShowOverlay(false), 2000);
        } else {
          setError(detail);
        }
        throw err;
      }
    },
    [selectedPlayer, setLogin, navigate],
  );

  const cancelLogin = useCallback(() => {
    setShowOverlay(false);
    setSelectedPlayer(null);
    setError(null);
    setLockedMessage(null);
  }, []);

  return {
    players, selectedPlayer, showOverlay, error, lockedMessage,
    selectPlayer, submitLogin, cancelLogin,
  };
}
