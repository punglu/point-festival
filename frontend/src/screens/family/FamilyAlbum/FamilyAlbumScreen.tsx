import styles from './FamilyAlbumScreen.module.css';
import type { FamilyAlbumProps } from './types';

export function FamilyAlbumScreen({ model, onBack, onSearch, onUpload, onFilter, onSelectPhoto, onSelectAlbum }: FamilyAlbumProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1h">
      <section className={styles.content}>
        <header>
          <button type="button" onClick={onBack}>←</button>
          <div><h1>앨범</h1><span>{model.summary}</span></div>
          <button type="button" onClick={onSearch}>⌕</button>
          <button type="button" className={styles.cta} onClick={onUpload}>＋ 사진 올리기</button>
        </header>
        <div className={styles.filters}>
          {model.filters.map((f) => (
            <button type="button" key={f} className={f === model.activeFilter ? styles.selected : ''} onClick={() => onFilter?.(f)}>{f}</button>
          ))}
        </div>
        <section className={styles.hero}>
          <small>대표 사진 (16:9)</small>
          <div><span>이번 주 하이라이트</span><h2>{model.heroTitle}</h2><p>{model.heroMeta}</p></div>
          <button type="button">모두 보기</button>
        </section>
        <section className={styles.section}>
          <header><b>최근 추가된 사진</b><span>{model.recentMeta}</span></header>
          <div className={styles.photoGrid}>
            {model.recentPhotos.map((photo, index) => (
              <button key={photo} type="button" onClick={() => onSelectPhoto?.(photo)} className={index === 5 ? styles.more : ''}>
                {photo}{index === 2 && <i>▶</i>}
              </button>
            ))}
          </div>
        </section>
        <section className={styles.section}>
          <header><b>가족 앨범</b><span>전체 보기 ›</span></header>
          <div className={styles.albumGrid}>
            {model.albums.map((a) => (
              <article key={a.title} onClick={() => onSelectAlbum?.(a)} role="button" tabIndex={0}>
                <div className={styles.cover} />
                <div><b>{a.title}</b><span>{a.meta}</span></div>
                <em>{a.person}</em>
              </article>
            ))}
            <button type="button" className={styles.create}>＋<b>앨범 만들기</b><span>주제별로 모아보기</span></button>
          </div>
        </section>
        <aside className={styles.notice}>▣<div><b>사진은 가족 구성원만 볼 수 있어요.</b><span>앨범별로 공개 범위를 따로 설정할 수 있습니다.</span></div></aside>
      </section>
    </main>
  );
}
