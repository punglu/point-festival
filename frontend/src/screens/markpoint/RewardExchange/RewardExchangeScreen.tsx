import styles from './RewardExchangeScreen.module.css';
import type { RewardExchangeProps } from './types';

export function RewardExchangeScreen({ model, onBack, onSearch, onFilter, onSelectReward }: RewardExchangeProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1l">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <div>
          <h1>보상 교환</h1>
          <span>모은 포인트로 원하는 보상을 받아보세요</span>
        </div>
        <button type="button" onClick={onSearch}>⌕</button>
      </header>
      <section className={styles.content}>
        <section className={styles.points}>
          <span>{model.playerName}의 보유 포인트</span>
          <strong>{model.balance}P</strong>
        </section>
        <div className={styles.filters}>
          {model.filters.map((f) => (
            <button type="button" key={f} className={f === model.activeFilter ? styles.selected : ''} onClick={() => onFilter?.(f)}>
              {f}
            </button>
          ))}
        </div>
        <section>
          <h2>교환 가능한 보상</h2>
          <div className={styles.rewards}>
            {model.rewards.map((r) => (
              <button type="button" key={r.name} onClick={() => onSelectReward?.(r)}>
                <i>{r.icon}</i>
                <div>
                  <b>{r.name}</b>
                  <span>{r.meta}</span>
                </div>
                <em className={r.unavailable ? styles.unavailable : ''}>{r.action}</em>
              </button>
            ))}
          </div>
        </section>
        <section>
          <h2>최근 교환 내역</h2>
          <div className={styles.history}>
            <i>♧</i>
            <div>
              <b>{model.historyName}</b>
              <span>{model.historyMeta}</span>
            </div>
            <strong>{model.historyAmount}</strong>
          </div>
        </section>
        <aside>
          ♧
          <div>
            <b>보상 교환은 보호자 승인 후 사용할 수 있어요.</b>
            <span>승인된 교환권은 내 활동에서 확인할 수 있습니다.</span>
          </div>
        </aside>
      </section>
    </main>
  );
}
