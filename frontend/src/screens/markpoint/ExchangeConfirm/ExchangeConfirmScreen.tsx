import styles from './ExchangeConfirmScreen.module.css';
import type { ExchangeConfirmProps } from './types';

export function ExchangeConfirmScreen({ model, onCancel, onConfirm }: ExchangeConfirmProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="2h">
      <div className={styles.backdrop}>
        <span>보상 교환</span>
      </div>
      <div className={styles.overlay}>
        <div className={styles.modal}>
          <div className={styles.icon}>{model.icon}</div>
          <h1>{model.rewardName}로 교환할까요?</h1>
          <p>{model.note}</p>
          <article>
            <span>보유 포인트</span>
            <b>{model.currentBalance}P <i>→</i> <em>{model.balanceAfter}P</em></b>
          </article>
          <div className={styles.actions}>
            <button type="button" className={styles.secondary} onClick={onCancel}>취소</button>
            <button type="button" onClick={onConfirm}>{model.cost}P로 교환</button>
          </div>
        </div>
      </div>
    </main>
  );
}
