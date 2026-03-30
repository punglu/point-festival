import { useState } from 'react';
import styles from '../Auth.module.css';
import PinInput from './PinInput';
import { Button } from '../../../shared/components/Button';

interface Props {
  playerName: string;
  lastLogin: string | null;
  onSubmit: (pin: string, rememberMe: boolean) => Promise<void>;
  onCancel: () => void;
  error: string | null;
  lockedMessage: string | null;
}

export default function LoginOverlay({
  playerName, lastLogin, onSubmit, onCancel, error, lockedMessage,
}: Props) {
  const [rememberMe, setRememberMe] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [resetKey, setResetKey] = useState(0);

  const handlePinComplete = async (pin: string) => {
    setHasError(false);
    try {
      await onSubmit(pin, rememberMe);
    } catch {
      setHasError(true);
      setTimeout(() => {
        setHasError(false);
        setResetKey((k) => k + 1);
      }, 400);
    }
  };

  return (
    <div className={styles.loginOverlay}>
      <div className={styles.loginCard}>
        <h2 className={styles.loginCardTitle}>{playerName}</h2>
        <p className={styles.subtitle}>PIN 번호를 입력하세요</p>

        <PinInput onComplete={handlePinComplete} hasError={hasError} resetKey={resetKey} />

        {error && <div className={styles.loginError}>{error}</div>}
        {lockedMessage && <div className={styles.loginLocked}>{lockedMessage}</div>}

        <div className={styles.autoLoginCheckbox}>
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
          />
          <label>로그인 상태 유지</label>
        </div>

        {lastLogin && (
          <div className={styles.lastLoginInfo}>마지막 접속: {lastLogin}</div>
        )}

        <div className={styles.loginButtons}>
          <Button variant="ghost" style={{ flex: 1 }} onClick={onCancel}>취소</Button>
          <Button variant="primary" style={{ flex: 1 }}>로그인</Button>
        </div>
      </div>
    </div>
  );
}
