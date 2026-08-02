import styles from './WidgetGalleryScreen.module.css';
import type { WidgetGalleryProps } from './types';
export function WidgetGalleryScreen({ model, onBack, onConfirm, onSelectSize }: WidgetGalleryProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="3k" data-canonical-screen-label="위젯 갤러리" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <div>
          <h1>{model.title}</h1>
          <span>{model.subtitle}</span>
        </div>
      </header>
      <div className={styles.tabs}>
        {model.sizes.map((size) => (
          <button key={size} type="button" className={size === model.activeSize ? styles.tabOn : ''} onClick={() => onSelectSize?.(size)}>{size}</button>
        ))}
      </div>

      <span className={styles.label}>{model.point.label}</span>
      <div className={styles.pointWidget}>
        <div className={styles.avatar}>{model.point.name.slice(0, 1)}</div>
        <span className={styles.name}>{model.point.name}</span>
        <strong>{model.point.value}</strong>
        <small>{model.point.delta}</small>
      </div>

      <span className={styles.label}>{model.mission.label}</span>
      <div className={styles.missionWidget}>
        <div className={styles.missionHead}>
          <b>{model.mission.title}</b>
          <span>{model.mission.progress}</span>
        </div>
        {model.mission.items.map((item) => (
          <div key={item.text} className={styles.missionItem}>
            <i className={item.done ? styles.checked : styles.unchecked} />
            <span>{item.text}</span>
          </div>
        ))}
      </div>

      <span className={styles.label}>{model.schedule.label}</span>
      <div className={styles.scheduleWidget}>
        <b>{model.schedule.title}</b>
        {model.schedule.items.map((item) => (
          <div key={item.text} className={styles.scheduleItem}>
            <i className={styles[item.color]} />
            <span>{item.text}</span>
            <em>{item.date}</em>
          </div>
        ))}
      </div>

      <button type="button" className={styles.confirm} onClick={onConfirm}>{model.confirmLabel}</button>
    </main>
  );
}
