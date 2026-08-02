import styles from './PinInitialSetupScreen.module.css';
import type { PinInitialSetupProps } from './types';
export function PinInitialSetupScreen({ model, onKeyPress, onBack }: PinInitialSetupProps) {
  const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫'];
  return (
    <main className={styles.screen} data-canonical-screen-id="2s" data-canonical-screen-label="PIN 최초 설정" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>←</button>
      </header>
      <section className={styles.hero}>
        <div className={styles.lock}>🔒</div>
        <h1 className={styles.title}>{model.title}</h1>
        <p>{model.description}</p>
      </section>
      <div className={styles.card}>
        <span className={styles.step}>{model.step}</span>
        <div className={styles.dots}>
          {Array.from({ length: model.dotCount }, (_, i) => (
            <i key={i} className={i < model.filledCount ? styles.filled : ''} />
          ))}
        </div>
        <div className={styles.keypad}>
          {keys.map((key, i) => (key ? <button key={key} type="button" onClick={() => onKeyPress?.(key)}>{key}</button> : <span key={`blank-${i}`} />))}
        </div>
        <span className={styles.hint}>{model.hint}</span>
      </div>
    </main>
  );
}
