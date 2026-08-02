import styles from './ScheduleDetailScreen.module.css';
import type { ScheduleDetailProps } from './types';
export function ScheduleDetailScreen({ model, onBack, onEdit, onDelete }: ScheduleDetailProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="2u" data-canonical-screen-label="일정 상세" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>일정 상세</h1>
        <span className={styles.more}>⋯</span>
      </header>
      <section className={styles.hero}>
        <span className={styles.badge}>{model.category}</span>
        <h2>{model.title}</h2>
        <p>{model.dateTime}</p>
      </section>
      <section className={styles.card}>
        <div className={styles.row}><i>📍</i><span>{model.place}</span></div>
        <div className={styles.row}><i>🔁</i><span>{model.repeat}</span></div>
      </section>
      <section>
        <h3 className={styles.membersTitle}>참석자</h3>
        <div className={styles.card}>
          {model.attendees.map((a) => (
            <div className={styles.row} key={a.name}>
              <i className={styles[a.tone]}>{a.name}</i>
              <span>{a.name}</span>
            </div>
          ))}
        </div>
      </section>
      <div className={styles.actions}>
        <button type="button" className={styles.delete} onClick={onDelete}>삭제</button>
        <button type="button" className={styles.edit} onClick={onEdit}>수정하기</button>
      </div>
    </main>
  );
}
