import styles from './AlbumSearchScreen.module.css';
import type { AlbumSearchProps } from './types';

export function AlbumSearchScreen({ model, onBack, onCancel, onClearQuery, onSelectAlbum, onSelectPhoto, onSelectRecent }: AlbumSearchProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1w">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <div className={styles.search}>⌕ <span>{model.query}</span><button type="button" onClick={onClearQuery}>×</button></div>
        <button type="button" onClick={onCancel}>취소</button>
      </header>
      <section>
        <span className={styles.summary}>{model.summary}</span>
        <h2>앨범</h2>
        <article onClick={onSelectAlbum} role="button" tabIndex={0}>
          <div />
          <section><b>{model.albumTitle}</b><span>{model.albumMeta}</span></section>
          <em>›</em>
        </article>
        <h2>사진</h2>
        <div className={styles.grid}>
          {model.photos.map((photo) => <button key={photo} type="button" onClick={() => onSelectPhoto?.(photo)}>{photo}</button>)}
        </div>
        <h2>최근 검색어</h2>
        <div className={styles.recent}>
          {model.recentSearches.map((r) => <span key={r} onClick={() => onSelectRecent?.(r)}>{r}</span>)}
        </div>
      </section>
    </main>
  );
}
