import styles from './MissionDetailScreen.module.css';
import type { MissionDetailProps } from './types';

export function MissionDetailScreen({ model, onBack, onMenu, onSubmit }: MissionDetailProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1k">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>미션 상세</h1>
        <button type="button" onClick={onMenu}>⋮</button>
      </header>
      <section className={styles.content}>
        <article className={styles.mission}>
          <span>오늘의 미션</span>
          <div>
            <div>
              <h2>{model.title}</h2>
              <p>{model.description}</p>
            </div>
            <strong>{model.reward}</strong>
          </div>
          <i><b style={{ width: `${model.progressPercent}%` }} /></i>
          <footer>{model.completedCount}/{model.totalCount} 완료</footer>
        </article>
        <section className={styles.card}>
          <h3>체크리스트</h3>
          {model.checklist.map((item) => (
            <div className={styles.check} key={item.label}>
              <i className={item.done ? styles.checked : ''}>{item.done ? '✓' : ''}</i>
              <span className={item.done ? styles.complete : ''}>{item.label}</span>
            </div>
          ))}
        </section>
        <section className={styles.card}>
          <h3>완료 인증 사진</h3>
          <div className={styles.photo}>인증사진</div>
          <p>{model.photoNotice}</p>
        </section>
        <aside>☑<span>{model.submitNotice}</span></aside>
      </section>
      <button type="button" className={styles.submit} onClick={onSubmit}>완료 인증 제출하기</button>
    </main>
  );
}
