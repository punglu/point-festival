import { useEffect, useState } from 'react';
import styles from './PinChangeScreen.module.css';

export type PinChangeProps = {
  onBack?: () => void;
  onComplete?: () => void;
};

export function PinChangeScreen({ onBack, onComplete }: PinChangeProps) {
  const [step, setStep] = useState(0);
  const [value, setValue] = useState('');
  const titles = ['현재 PIN을 입력해 주세요', '새 PIN을 입력해 주세요', '새 PIN을 다시 입력해 주세요'];
  const subtitles = ['본인 확인 후 새 PIN을 설정할 수 있어요', '4자리 번호를 입력해 주세요', '입력하신 PIN을 한 번 더 확인해요'];

  useEffect(() => {
    if (value.length !== 4) return;
    const timer = setTimeout(() => {
      if (step === 2) {
        // Real PIN-change API does not exist yet — completion callback only
        // advances the local flow, per the W7.4 data-wiring boundary.
        onComplete?.();
        return;
      }
      setStep((s) => Math.min(2, s + 1));
      setValue('');
    }, 200);
    return () => clearTimeout(timer);
  }, [value, step, onComplete]);

  return (
    <main className={styles.page} data-canonical-screen-id="1u">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>PIN 변경</h1>
      </header>
      <section>
        <div className={styles.progress}>
          {[0, 1, 2].map((i) => <i key={i} className={i <= step ? styles.on : ''} />)}
        </div>
        <div className={styles.lock}>🔒</div>
        <h2>{titles[step]}</h2>
        <p>{subtitles[step]}</p>
        <div className={styles.dots}>{[0, 1, 2, 3].map((i) => <i key={i} className={i < value.length ? styles.filled : ''} />)}</div>
        <div className={styles.keys}>
          {['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫'].map((key, i) => (
            key ? (
              <button key={key} type="button" onClick={() => (key === '⌫' ? setValue((v) => v.slice(0, -1)) : setValue((v) => (v + key).slice(0, 4)))}>{key}</button>
            ) : <span key={`blank-${i}`} />
          ))}
        </div>
        <span className={styles.forgot}>PIN을 잊으셨나요?</span>
      </section>
    </main>
  );
}
