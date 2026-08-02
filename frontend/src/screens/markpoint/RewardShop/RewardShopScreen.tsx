import styles from './RewardShopScreen.module.css';
import type { RewardShopProps } from './types';

export function RewardShopScreen({ model, onFilter, onSelectReward }: RewardShopProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="2j">
      <header>
        <i className={styles.avatar}>{model.playerInitial}</i>
        <div>
          <h1>리워드샵</h1>
          <span>모은 포인트로 원하는 보상을 골라보세요</span>
        </div>
      </header>
      <section>
        <div className={styles.banner}>
          <span>내 포인트</span>
          <b>{model.balance}P</b>
          <i className={styles.star}>★</i>
        </div>
        <div className={styles.filters}>
          {model.filters.map((f) => (
            <button type="button" key={f} className={f === model.activeFilter ? styles.active : ''} onClick={() => onFilter?.(f)}>
              {f}
            </button>
          ))}
        </div>
        <div className={styles.grid}>
          {model.rewards.map((r) => (
            <article key={r.name} className={r.available ? '' : styles.disabled}>
              <i>{r.icon}</i>
              <b>{r.name}</b>
              {r.available ? (
                <button type="button" onClick={() => onSelectReward?.(r)}>{r.cost}P</button>
              ) : (
                <span className={styles.need}>{r.cost}P 필요</span>
              )}
            </article>
          ))}
        </div>
        <h2>내가 교환한 것들</h2>
        <article className={styles.history}>
          <i>🍬</i>
          <div>
            <b>{model.historyName}</b>
            <span>{model.historyMeta}</span>
          </div>
          <em>{model.historyAmount}</em>
        </article>
      </section>
    </main>
  );
}
