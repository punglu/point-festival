import styles from './ThemeSettingsScreen.module.css';
import type { ThemeSettingsProps } from './types';
export function ThemeSettingsScreen({ model, onBack, onSelectMode, onToggle }: ThemeSettingsProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="3g" data-canonical-screen-label="화면 테마 설정" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>{model.title}</h1>
      </header>
      <span className={styles.label}>모드</span>
      <div className={styles.modes}>
        {model.modes.map((mode) => (
          <button
            key={mode.label}
            type="button"
            className={mode.selected ? styles.modeOn : styles.mode}
            onClick={() => onSelectMode?.(mode.label)}
          >
            <i className={mode.label === '다크' ? styles.swatchDark : mode.label === '시스템 설정' ? styles.swatchSystem : styles.swatchLight} />
            <span>{mode.label}</span>
          </button>
        ))}
      </div>
      <div className={styles.card}>
        <button type="button" onClick={() => onToggle?.('largeText')}>
          <span>큰 글씨 모드</span>
          <i className={model.largeText ? styles.on : styles.off} />
        </button>
        <button type="button" onClick={() => onToggle?.('highContrast')}>
          <span>고대비 모드</span>
          <i className={model.highContrast ? styles.on : styles.off} />
        </button>
      </div>
      <span className={styles.label}>글자 크기</span>
      <div className={styles.previewCard}>
        <strong>{model.previewText}</strong>
        <div className={styles.slider}>
          <span>가</span>
          <input type="range" min={0} max={100} defaultValue={model.fontScale} readOnly />
          <span className={styles.big}>가</span>
        </div>
      </div>
    </main>
  );
}
