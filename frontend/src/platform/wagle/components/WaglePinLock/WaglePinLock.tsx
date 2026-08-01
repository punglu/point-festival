/**
 * Wagle device screen lock.
 *
 * This gates **conversation content on this device**, and nothing else. While
 * it is showing:
 *
 * - the Account Session stays live,
 * - Markpoint and the Family screens stay reachable,
 * - Push subscriptions stay active and notifications keep arriving.
 *
 * All three are contract, not incidental. A lock that logged the user out or
 * silenced their notifications would turn a convenience feature into a
 * platform-wide outage triggered by a mistyped PIN.
 *
 * Recovery is **reset, never retrieval**. There is no "show my PIN" path here
 * because there is no server endpoint that could answer it.
 */
import { useEffect, useState } from 'react';

import {
  getDevicePinStatus,
  resetDevicePin,
  setDevicePin,
  verifyDevicePin,
  type DevicePinStatus,
} from '../../realtime/wagleDeviceApi';
import styles from './WaglePinLock.module.css';

type Mode = 'loading' | 'unlocked' | 'locked' | 'setup' | 'reset';

interface Props {
  children: React.ReactNode;
  /** Escape hatch to the rest of the platform while locked. */
  onLeave?: () => void;
}

export function WaglePinLock({ children, onLeave }: Props) {
  const [mode, setMode] = useState<Mode>('loading');
  const [status, setStatus] = useState<DevicePinStatus | null>(null);
  const [pin, setPin] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getDevicePinStatus()
      .then((next) => {
        if (cancelled) return;
        setStatus(next);
        setMode(next.configured ? 'locked' : 'unlocked');
      })
      .catch(() => {
        // A status lookup failure must not lock the user out of their own
        // conversations — failing open here is the safe direction, because the
        // lock is a local convenience and the server still authorizes every
        // request that actually returns content.
        if (!cancelled) setMode('unlocked');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const submitUnlock = async () => {
    setBusy(true);
    setError(null);
    try {
      await verifyDevicePin(pin);
      setPin('');
      setMode('unlocked');
    } catch (err: unknown) {
      const response = (err as { response?: { status?: number; data?: { detail?: string } } })
        .response;
      if (response?.status === 423) {
        setError('시도 횟수를 초과했어요. 잠시 후 다시 시도하거나 PIN을 재설정해주세요.');
      } else {
        setError(response?.data?.detail ?? 'PIN이 올바르지 않아요');
      }
      setPin('');
      try {
        setStatus(await getDevicePinStatus());
      } catch {
        /* status refresh is advisory */
      }
    } finally {
      setBusy(false);
    }
  };

  const submitNewPin = async (kind: 'setup' | 'reset') => {
    setBusy(true);
    setError(null);
    try {
      const next = kind === 'setup' ? await setDevicePin(pin) : await resetDevicePin(pin);
      setStatus(next);
      setPin('');
      setMode('unlocked');
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setError(detail ?? 'PIN을 설정할 수 없어요');
    } finally {
      setBusy(false);
    }
  };

  if (mode === 'loading') {
    return <div className={styles.gate} aria-busy="true" />;
  }

  if (mode === 'unlocked') {
    return <>{children}</>;
  }

  const heading =
    mode === 'locked' ? '와글와글 잠금' : mode === 'reset' ? 'PIN 재설정' : 'PIN 설정';

  return (
    <section className={styles.gate} role="dialog" aria-modal="true" aria-label={heading}>
      <div className={styles.panel}>
        <h1 className={styles.title}>{heading}</h1>
        <p className={styles.help}>
          {mode === 'locked'
            ? '이 기기에서 대화를 보려면 PIN을 입력해주세요.'
            : '이 기기에서만 사용할 PIN을 입력해주세요.'}
        </p>

        <label className={styles.label} htmlFor="wagle-pin">
          PIN
        </label>
        <input
          id="wagle-pin"
          className={styles.input}
          type="password"
          inputMode="numeric"
          autoComplete="off"
          value={pin}
          disabled={busy}
          onChange={(event) => setPin(event.target.value.replace(/\D/g, ''))}
          onKeyDown={(event) => {
            if (event.key !== 'Enter') return;
            if (mode === 'locked') void submitUnlock();
            else void submitNewPin(mode === 'reset' ? 'reset' : 'setup');
          }}
        />

        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}
        {status?.remaining_attempts !== null && status?.remaining_attempts !== undefined && mode === 'locked' && (
          <p className={styles.meta}>남은 시도 {status.remaining_attempts}회</p>
        )}

        <div className={styles.actions}>
          <button
            type="button"
            className={styles.primary}
            disabled={busy || pin.length === 0}
            onClick={() => {
              if (mode === 'locked') void submitUnlock();
              else void submitNewPin(mode === 'reset' ? 'reset' : 'setup');
            }}
          >
            {mode === 'locked' ? '잠금 해제' : '저장'}
          </button>

          {mode === 'locked' && (
            <button
              type="button"
              className={styles.secondary}
              disabled={busy}
              onClick={() => {
                setPin('');
                setError(null);
                setMode('reset');
              }}
            >
              PIN을 잊었어요
            </button>
          )}
        </div>

        {/* Leaving Wagle is always available: the lock covers this screen, not
            the platform. Markpoint and the Family screens stay reachable. */}
        {onLeave && (
          <button type="button" className={styles.leave} onClick={onLeave}>
            다른 화면으로 이동
          </button>
        )}
      </div>
    </section>
  );
}
