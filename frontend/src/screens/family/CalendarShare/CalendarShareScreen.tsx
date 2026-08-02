import styles from './CalendarShareScreen.module.css';
import type { CalendarShareProps } from './types';
export function CalendarShareScreen({ model, onClose, onShare, onToggleIntegration }: CalendarShareProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="3a" data-canonical-screen-label="가족 캘린더 공유" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onClose}>←</button>
        <h1>{model.title}</h1>
      </header>
      <div className={styles.linkBox}>
        <span className={styles.linkLabel}>외부 캘린더 구독 링크</span>
        <div className={styles.linkRow}>
          <span className={styles.link}>{model.subscriptionLink}</span>
          <span className={styles.copy}>{model.copyLabel}</span>
        </div>
      </div>
      <div className={styles.group}>
        <span className={styles.groupLabel}>연동할 앱</span>
        <div className={styles.card}>
          {model.integrations.map((it) => (
            <button type="button" key={it.name} className={styles.row} onClick={() => onToggleIntegration?.(it.name)}>
              <i className={styles.appIcon}>▦</i>
              <span>{it.name}</span>
              <em className={it.on ? styles.on : styles.off} />
            </button>
          ))}
        </div>
      </div>
      <div className={styles.group}>
        <span className={styles.groupLabel}>공유 대상</span>
        <div className={styles.card}>
          {model.targets.map((t) => (
            <div className={styles.row} key={t.name}>
              <i className={styles.avatar}>{t.name}</i>
              <span>{t.name}</span>
              <em className={styles.shared}>{t.shared ? '공유됨' : ''}</em>
            </div>
          ))}
        </div>
      </div>
      <button type="button" className={styles.confirm} onClick={onShare}>{model.confirmLabel}</button>
      <div className={styles.homeBar} />
    </main>
  );
}
