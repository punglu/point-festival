import styles from './FileViewerScreen.module.css';
import type { FileViewerProps } from './types';

export function FileViewerScreen({ model, onBack, onSelectMode, onTab, onSelectFile }: FileViewerProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="2b">
      <header>
        <button type="button" onClick={onBack} aria-label="뒤로">←</button>
        <div>
          <h1>{model.title}</h1>
          <span>{model.subtitle}</span>
        </div>
        <button type="button" onClick={onSelectMode}>선택</button>
      </header>
      <section>
        <div className={styles.tabs}>
          {model.tabs.map((tab) => (
            <button
              type="button"
              key={tab}
              className={tab === model.activeTab ? styles.active : ''}
              onClick={() => onTab?.(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
        <h2>최근 파일</h2>
        <div className={styles.grid}>
          {model.recentFiles.map((file) => (
            <button
              key={file.label}
              type="button"
              onClick={() => onSelectFile?.(file)}
              className={file.isFile ? styles.file : ''}
            >
              {file.label}
            </button>
          ))}
        </div>
        <h2>{model.todaySectionLabel}</h2>
        <div className={styles.grid}>
          {model.todayFiles.map((file) => (
            <button key={file.label} type="button" onClick={() => onSelectFile?.(file)}>
              {file.label}
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}
