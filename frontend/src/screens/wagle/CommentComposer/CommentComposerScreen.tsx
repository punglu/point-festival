import { useState } from 'react';
import styles from './CommentComposerScreen.module.css';
import type { CommentComposerProps } from './types';
export function CommentComposerScreen({ model, onSubmit, onCancel }: CommentComposerProps) {
  const [text, setText] = useState('');
  return (
    <main className={styles.screen} data-canonical-screen-id="3d" data-canonical-screen-label="댓글 작성" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onCancel}>←</button>
        <h1>댓글 {model.commentCount}개</h1>
      </header>
      <div className={styles.post}>
        <div className={styles.postHead}>
          <span className={styles.badge}>{model.post.badge}</span>
          <i className={styles.avatar}>{model.post.author}</i>
          <span className={styles.author}>{model.post.author}</span>
          <span className={styles.time}>{model.post.time}</span>
        </div>
        <strong>{model.post.title}</strong>
        <p>{model.post.body}</p>
      </div>
      <div className={styles.comments}>
        {model.comments.map((c) => (
          <div className={styles.comment} key={c.author + c.message}>
            <i className={styles.avatar}>{c.author}</i>
            <div className={styles.commentBody}>
              <div className={styles.bubble}>
                <span className={styles.author}>{c.author}</span>
                <span className={styles.message}>{c.message}</span>
              </div>
              <div className={styles.meta}>
                <span>{c.time}</span>
                <span className={styles.reply}>답글</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className={styles.composer}>
        <div className={styles.composerBar}>
          <i className={styles.avatar}>{model.myInitial}</i>
          <input value={text} onChange={(e) => setText(e.target.value)} placeholder={model.placeholder} />
          <button type="button" className={styles.send} onClick={() => onSubmit?.(text)}>➤</button>
        </div>
      </div>
    </main>
  );
}
