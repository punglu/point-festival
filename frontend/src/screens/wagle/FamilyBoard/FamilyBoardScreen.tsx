import styles from './FamilyBoardScreen.module.css';
import type { FamilyBoardProps } from './types';
export function FamilyBoardScreen({ model, onWrite, onBack, onTab, onSelectPost }: FamilyBoardProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="3c" data-canonical-screen-label="가족 게시판" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <div>
          <h1>가족 게시판</h1>
          <span className={styles.subtitle}>{model.subtitle}</span>
        </div>
        <button type="button" className={styles.write} onClick={onWrite}>＋ 글쓰기</button>
      </header>
      <nav className={styles.tabs}>
        {model.tabs.map((t) => (
          <button key={t} type="button" className={t === model.activeTab ? styles.tabOn : ''} onClick={() => onTab?.(t)}>{t}</button>
        ))}
      </nav>
      <section className={styles.list}>
        {model.posts.map((post) => (
          <article
            key={post.title}
            onClick={() => onSelectPost?.(post)}
            role={onSelectPost ? 'button' : undefined}
            tabIndex={onSelectPost ? 0 : undefined}
          >
            <div className={styles.meta}>
              <span className={styles[post.badgeTone]}>{post.badge}</span>
              <i>{post.author}</i>
              <b>{post.author}</b>
              <time>{post.time}</time>
            </div>
            <h2>{post.title}</h2>
            {post.summary && <p>{post.summary}</p>}
            <footer>♡ {post.likes} · 💬 {post.comments}개 댓글</footer>
          </article>
        ))}
      </section>
    </main>
  );
}
