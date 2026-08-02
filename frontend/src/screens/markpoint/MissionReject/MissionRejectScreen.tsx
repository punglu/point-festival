import styles from './MissionRejectScreen.module.css';
import type { MissionRejectProps } from './types';

export function MissionRejectScreen({ model, onBack, onRetry }: MissionRejectProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1s">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>미션 알림</h1>
      </header>
      <section>
        <div className={styles.hero}>
          <div className={styles.icon}>✕</div>
          <div>
            <strong>미션이 반려되었어요</strong>
            <span>다시 시도해서 인증해 보세요</span>
          </div>
        </div>
        <article className={styles.mission}>
          <i>{model.missionIcon}</i>
          <div>
            <b>{model.missionTitle}</b>
            <span>{model.missionSummary}</span>
          </div>
        </article>
        <article className={styles.reason}>
          <div className={styles.reasonHead}>
            <i>{model.reviewerName}</i>
            <b>{model.reviewerName}의 반려 사유</b>
          </div>
          <p>{model.reason}</p>
        </article>
        <article className={styles.photo}>
          <span>제출했던 사진</span>
          <div>반려된 인증사진</div>
        </article>
        <button type="button" className={styles.retry} onClick={onRetry}>다시 인증하기</button>
      </section>
    </main>
  );
}
