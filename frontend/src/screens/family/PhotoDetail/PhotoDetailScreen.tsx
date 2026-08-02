import styles from './PhotoDetailScreen.module.css';
import type { PhotoDetailProps } from './types';

export function PhotoDetailScreen({ model, onClose, onMenu, onPrev, onNext }: PhotoDetailProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1p">
      <header>
        <button type="button" onClick={onClose}>✕</button>
        <div>
          <b>{model.title}</b>
          <span>{model.meta}</span>
        </div>
        <button type="button" onClick={onMenu}>⋯</button>
      </header>
      <section className={styles.photo}>
        <i className={styles.prev} onClick={onPrev}>‹</i>
        <span>원본 사진</span>
        <i className={styles.next} onClick={onNext}>›</i>
      </section>
      <footer>
        <div className={styles.actions}>
          <span><i>♥</i>{model.likeCount}</span>
          <span><i>💬</i>{model.commentCount}</span>
          <i className={styles.bookmark}>🔖</i>
        </div>
        <div className={styles.comment}>
          <b>{model.commentAuthor}</b>
          <span>{model.commentText}</span>
        </div>
        <div className={styles.input}>
          <span>댓글 달기...</span>
          <i>➤</i>
        </div>
      </footer>
    </main>
  );
}
