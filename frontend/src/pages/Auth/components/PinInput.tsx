import { useState, useEffect } from 'react';
import styles from '../Auth.module.css';

interface PinInputProps {
  onComplete: (pin: string) => void;
  hasError: boolean;
  resetKey: number;
}

const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫'];

export default function PinInput({ onComplete, hasError, resetKey }: PinInputProps) {
  const [digits, setDigits] = useState<string[]>(['', '', '', '']);

  useEffect(() => {
    setDigits(['', '', '', '']);
  }, [resetKey]);

  const addDigit = (digit: string) => {
    setDigits(prev => {
      const next = [...prev];
      const emptyIdx = next.findIndex(d => d === '');
      if (emptyIdx === -1) return prev;
      next[emptyIdx] = digit;
      if (emptyIdx === 3) {
        setTimeout(() => onComplete(next.join('')), 300);
      }
      return next;
    });
  };

  const removeDigit = () => {
    setDigits(prev => {
      const next = [...prev];
      for (let i = 3; i >= 0; i--) {
        if (next[i] !== '') {
          next[i] = '';
          break;
        }
      }
      return next;
    });
  };

  return (
    <>
      {/* PIN 슬롯 */}
      <div className={styles.pinSlots}>
        {digits.map((d, i) => (
          <div
            key={i}
            className={`${styles.pinSlot} ${d ? styles.pinSlotFilled : ''} ${hasError ? styles.pinSlotError : ''}`}
          >
            {d ? '●' : ''}
          </div>
        ))}
      </div>

      {/* 숫자 키패드 */}
      <div className={styles.keypad}>
        {KEYS.map((k, i) => {
          if (k === '') {
            return <div key={i} className={styles.keyEmpty} />;
          }
          if (k === '⌫') {
            return (
              <button
                key={i}
                type="button"
                className={`${styles.key} ${styles.keyBackspace}`}
                onClick={removeDigit}
              >
                ⌫
              </button>
            );
          }
          return (
            <button
              key={i}
              type="button"
              className={styles.key}
              onClick={() => addDigit(k)}
            >
              {k}
            </button>
          );
        })}
      </div>
    </>
  );
}
