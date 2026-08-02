import styles from './LanguageSettingsScreen.module.css';
import type { LanguageSettingsProps } from './types';
export function LanguageSettingsScreen({ model, onBack, onSelect }: LanguageSettingsProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="3f" data-canonical-screen-label="언어 설정" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>{model.title}</h1>
      </header>
      <section className={styles.list}>
        {model.options.map((option) => (
          <button key={option.label} type="button" onClick={() => onSelect?.(option.label)}>
            <span>{option.label}</span>
            <i className={option.selected ? styles.on : styles.off} />
          </button>
        ))}
      </section>
      <aside className={styles.notice}>
        <span>?</span>
        <p>{model.notice}</p>
      </aside>
    </main>
  );
}
