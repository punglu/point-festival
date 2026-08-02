import styles from './FamilyActivityLogScreen.module.css';
import type { FamilyActivityLogProps } from './types';
export function FamilyActivityLogScreen({ model, onBack, onFilter }: FamilyActivityLogProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="2r" data-canonical-screen-label="가족 활동 로그" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>{model.title}</h1>
      </header>
      <div className={styles.filters}>
        {model.filters.map((f) => (
          <button type="button" key={f} className={f === model.activeFilter ? styles.filterOn : styles.filter} onClick={() => onFilter?.(f)}>{f}</button>
        ))}
      </div>
      {model.days.map((day) => (
        <div className={styles.group} key={day.label}>
          <span className={styles.groupLabel}>{day.label}</span>
          <div className={styles.card}>
            {day.events.map((ev) => (
              <div className={styles.row} key={ev.title}>
                <i className={styles[ev.tone]}>{ev.initial}</i>
                <div>
                  <strong>{ev.title}</strong>
                  {ev.detail && <span>{ev.detail}</span>}
                </div>
                <time>{ev.time}</time>
              </div>
            ))}
          </div>
        </div>
      ))}
    </main>
  );
}
