import styles from './SearchAllScreen.module.css';
import type { SearchAllProps } from './types';
export function SearchAllScreen({ model, onBack, onCancel, onFilter }: SearchAllProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="3j" data-canonical-screen-label="검색 전체" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <div className={styles.searchBox}>
          <i>🔍</i>
          <span>{model.query}</span>
        </div>
        <button type="button" className={styles.cancel} onClick={onCancel}>{model.cancelLabel}</button>
      </header>
      <div className={styles.filters}>
        {model.filters.map((f) => (
          <button type="button" key={f} className={f === model.activeFilter ? styles.filterOn : styles.filter} onClick={() => onFilter?.(f)}>{f}</button>
        ))}
      </div>
      {model.groups.map((group) => (
        <div className={styles.group} key={group.label}>
          <span className={styles.groupLabel}>{group.label}</span>
          <div className={styles.card}>
            {group.items.map((item, i) => (
              <div className={styles.row} key={i}>
                <i className={styles[item.iconTone]}>{item.icon}</i>
                <div>
                  <span>
                    {item.titleParts.map((part, j) => (typeof part === 'string' ? part : <b key={j}>{part.hl}</b>))}
                  </span>
                  <small>{item.meta}</small>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
      <div className={styles.group}>
        <span className={styles.groupLabel}>최근 검색어</span>
        <div className={styles.recent}>
          {model.recentSearches.map((r) => (
            <span key={r}>{r}</span>
          ))}
        </div>
      </div>
    </main>
  );
}
