import styles from './ShortcutEditorScreen.module.css';
import type { ShortcutEditorProps } from './types';
export function ShortcutEditorScreen({ model, onBack, onConfirm, onToggle }: ShortcutEditorProps) {
  const selected = model.items.filter((i) => i.selected);
  const rest = model.items.filter((i) => !i.selected);
  return (
    <main className={styles.screen} data-canonical-screen-id="3l" data-canonical-screen-label="바로가기 편집" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>✕</button>
        <h1>{model.title}</h1>
        <button type="button" className={styles.done} onClick={onConfirm}>{model.confirmLabel}</button>
      </header>
      <p className={styles.subtitle}>{model.subtitle}</p>
      <span className={styles.label}>{model.selectedLabel}</span>
      <div className={styles.grid}>
        {selected.map((item) => (
          <button key={item.label} type="button" className={styles.cardOn} onClick={() => onToggle?.(item.label)}>
            <i className={styles.check}>✓</i>
            <span className={styles.icon}>{item.icon}</span>
            <b>{item.label}</b>
          </button>
        ))}
      </div>
      <span className={styles.label}>{model.addMoreLabel}</span>
      <div className={styles.grid}>
        {rest.map((item) => (
          <button key={item.label} type="button" className={styles.card} onClick={() => onToggle?.(item.label)}>
            <span className={styles.icon}>{item.icon}</span>
            <b>{item.label}</b>
          </button>
        ))}
      </div>
    </main>
  );
}
