import styles from './PopularPostsScreen.module.css';
import type { PopularPostsProps } from './types';
export function PopularPostsScreen({ model, onSelect, onRangeChange }: PopularPostsProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="3e" data-canonical-screen-label="인기 게시글" data-canonical-source="wave7-full-authority">
      <header>
        <div>
          <h1>{model.title}</h1>
          <span className={styles.subtitle}>{model.subtitle}</span>
        </div>
      </header>
      <div className={styles.ranges}>
        {model.ranges.map((r) => (
          <button type="button" key={r} className={r === model.activeRange ? styles.rangeOn : styles.range} onClick={() => onRangeChange?.(r)}>{r}</button>
        ))}
      </div>
      {model.posts.map((post) => (
        <button type="button" key={post.rank} className={post.rank === 1 ? styles.top : styles.card} onClick={() => onSelect?.(post.rank)}>
          <div className={styles.rankRow}>
            <span className={post.rank === 1 ? styles.rankGold : styles.rankNumber}>{post.rank}</span>
            {post.rank === 1 ? <span className={styles.rankLabel}>이번 주 1위</span> : <span className={styles.badge}>{post.badge}</span>}
          </div>
          <strong>{post.title}</strong>
          <div className={styles.meta}>
            <i>{post.author}</i>
            <span>{post.author} · {post.time}</span>
            <span className={styles.stats}>
              <em>♥ {post.likes}</em>
              <em>💬 {post.comments}</em>
            </span>
          </div>
        </button>
      ))}
    </main>
  );
}
