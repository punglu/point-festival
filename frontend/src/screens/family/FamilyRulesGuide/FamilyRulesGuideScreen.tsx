import styles from './FamilyRulesGuideScreen.module.css';
import type { FamilyRulesGuideProps } from './types';
export function FamilyRulesGuideScreen({ model, onBack, onConfirm }: FamilyRulesGuideProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="2q" data-canonical-screen-label="가족 규칙 안내" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>{model.title}</h1>
      </header>
      <div className={styles.hero}>
        <span className={styles.heroIcon}>🛡</span>
        <strong>{model.heroTitle}</strong>
        <p>{model.heroBody}</p>
      </div>
      {model.groups.map((group) => (
        <div className={styles.group} key={group.label}>
          <span className={styles.groupLabel}>{group.label}</span>
          <div className={styles.card}>
            {group.items.map((item) => (
              <div className={styles.row} key={item.title}>
                <i className={styles[item.tone]}>✓</i>
                <div>
                  <strong>{item.title}</strong>
                  <span>{item.description}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
      <div className={styles.notice}>
        <i>ⓘ</i>
        <span>{model.notice}</span>
      </div>
      <button type="button" className={styles.confirm} onClick={onConfirm}>{model.confirmLabel}</button>
    </main>
  );
}
