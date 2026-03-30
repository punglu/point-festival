import { useRef, useCallback, useEffect } from 'react';
import styles from '../Auth.module.css';

interface PinInputProps {
  onComplete: (pin: string) => void;
  hasError: boolean;
  resetKey: number;
}

export default function PinInput({ onComplete, hasError, resetKey }: PinInputProps) {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const values = useRef<string[]>(['', '', '', '']);

  useEffect(() => {
    values.current = ['', '', '', ''];
    inputRefs.current.forEach((ref) => {
      if (ref) ref.value = '';
    });
    inputRefs.current[0]?.focus();
  }, [resetKey]);

  const getClassName = (index: number): string => {
    if (hasError) return styles.pinDigitError;
    if (values.current[index]) return styles.pinDigitFilled;
    return styles.pinDigit;
  };

  const handleInput = useCallback(
    (index: number, rawValue: string) => {
      const cleaned = rawValue.replace(/[^0-9]/g, '');
      values.current[index] = cleaned;
      const el = inputRefs.current[index];
      if (el) el.value = cleaned;

      if (cleaned && index < 3) {
        inputRefs.current[index + 1]?.focus();
      }

      if (index === 3 && cleaned) {
        const pin = values.current.join('');
        if (pin.length === 4) {
          setTimeout(() => onComplete(pin), 300);
        }
      }
    },
    [onComplete],
  );

  const handleKeyDown = useCallback((index: number, key: string) => {
    if (key === 'Backspace' && !values.current[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  }, []);

  return (
    <div className={styles.pinInputContainer}>
      {[0, 1, 2, 3].map((i) => (
        <input
          key={i}
          ref={(el) => { inputRefs.current[i] = el; }}
          type="text"
          maxLength={1}
          inputMode="numeric"
          pattern="[0-9]"
          autoComplete="off"
          className={getClassName(i)}
          onInput={(e) => handleInput(i, (e.target as HTMLInputElement).value)}
          onKeyDown={(e) => handleKeyDown(i, e.key)}
        />
      ))}
    </div>
  );
}
