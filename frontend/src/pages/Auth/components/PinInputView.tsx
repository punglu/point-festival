import { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from '../Auth.module.css';
import PinInput from './PinInput';
import { authApi } from '../api/authApi';
import { useAuthStore } from '../../../shared/stores/useAuthStore';
import { FALLBACK_COLORS } from '../constants';

interface Player {
  id: number;
  name: string;
  photo?: string | null;
}

interface Props {
  player: Player;
  onBack: () => void;
  onLoginError?: (msg: string) => void;
}

export default function PinInputView({ player, onBack, onLoginError }: Props) {
  const navigate = useNavigate();
  const { setLogin } = useAuthStore();
  const [error, setError] = useState<string | null>(null);
  const [lockedMessage, setLockedMessage] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);
  const [resetKey, setResetKey] = useState(0);
  const abortRef = useRef<AbortController | null>(null);

  const color = FALLBACK_COLORS[player.id % FALLBACK_COLORS.length];

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const handlePinComplete = useCallback(
    async (pin: string) => {
      setError(null);
      setHasError(false);

      abortRef.current?.abort();
      abortRef.current = new AbortController();

      try {
        const res = await authApi.login(
          { player_id: player.id, pin, remember_me: false },
          abortRef.current.signal,
        );

        setLogin(
          res.access_token,
          { id: res.player_id, name: res.player_name, role: res.player_role },
          res.is_admin ?? false,
        );

        navigate(res.is_admin ? '/admin' : '/dashboard');
      } catch (err: unknown) {
        const httpErr = err as { response?: { status?: number; data?: { detail?: string } }; name?: string };
        if (httpErr.name === 'AbortError' || httpErr.name === 'CanceledError') return;
        const httpStatus = httpErr.response?.status;
        const detail = httpErr.response?.data?.detail || '로그인 실패';

        if (onLoginError) {
          onLoginError(detail);
        } else if (httpStatus === 423) {
          setLockedMessage(detail);
        } else {
          setError(detail);
        }

        setHasError(true);
        setTimeout(() => {
          setHasError(false);
          setResetKey((k) => k + 1);
        }, 400);
      }
    },
    [player.id, setLogin, navigate, onLoginError],
  );

  const renderAvatarContent = () => {
    if (player.photo) {
      const src = player.photo.startsWith('data:')
        ? player.photo
        : `data:image/jpeg;base64,${player.photo}`;
      return <img src={src} alt={player.name} className={styles.pinAvatarPhoto} />;
    }
    return (
      <span
        className={styles.pinAvatarInitial}
        style={{ backgroundColor: color.bg, color: color.text }}
      >
        {player.name.charAt(0)}
      </span>
    );
  };

  return (
    <div className={styles.authView}>
      {/* Indigo 헤더: 플레이어 아바타 + 이름 */}
      <div className={styles.pinHeader}>
        <div className={styles.pinAvatar}>
          {renderAvatarContent()}
        </div>
        <div className={styles.pinPlayerName}>{player.name}</div>
        <div className={styles.pinPrompt}>PIN 번호를 입력하세요</div>
      </div>

      {/* PIN 슬롯 + 키패드 */}
      <div className={styles.pinBody}>
        <PinInput onComplete={handlePinComplete} hasError={hasError} resetKey={resetKey} />

        {error && <div className={styles.loginError}>{error}</div>}
        {lockedMessage && <div className={styles.loginLocked}>{lockedMessage}</div>}

        <button className={styles.backLink} onClick={onBack}>
          ← 다른 플레이어 선택
        </button>
      </div>
    </div>
  );
}
