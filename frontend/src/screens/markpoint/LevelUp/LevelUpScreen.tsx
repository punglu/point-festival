import styles from './LevelUpScreen.module.css';
import type { LevelUpProps } from './types';

export function LevelUpScreen({ model, onConfirm }: LevelUpProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="2c">
      <div className={styles.backdrop}>
        <span>홈</span>
      </div>
      <div className={styles.overlay}>
        <div className={styles.modal}>
          <span className={styles.eyebrow}>🎉 레벨 업!</span>
          <div className={styles.avatarWrap}>
            <div className={styles.avatar}>{model.playerInitial}</div>
            <span className={styles.badge}>{model.level}</span>
          </div>
          <div className={styles.text}>
            <strong>Lv.{model.level} {model.levelTitle} 달성!</strong>
            <p>
              {model.playerName}님, 축하해요!
              <br />
              더 많은 미션이 기다리고 있어요.
            </p>
          </div>
          <div className={styles.bonus}>
            <i>★</i>
            <span>보너스 +{model.bonusPoints}P 지급됨</span>
          </div>
          <button type="button" className={styles.confirm} onClick={onConfirm}>신난다!</button>
        </div>
      </div>
    </main>
  );
}
