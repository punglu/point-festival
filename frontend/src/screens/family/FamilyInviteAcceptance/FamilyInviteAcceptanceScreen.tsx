import mascot from '../../../assets/logos/family-platform-mascot.png';
import styles from './FamilyInviteAcceptanceScreen.module.css';
import type { FamilyInviteAcceptanceProps } from './types';
export function FamilyInviteAcceptanceScreen({ model, onAccept, onDecline }: FamilyInviteAcceptanceProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="2w" data-canonical-screen-label="가족 초대 수락" data-canonical-source="wave7-full-authority">
      <div className={styles.hero}>
        <img className={styles.logo} src={mascot} alt="브랜드 핀 로고" />
        <h1 className={styles.title}>우리 가족이 초대했어요</h1>
        <p>{model.inviter}님이 초대 코드를 보냈어요</p>
      </div>
      <div className={styles.card}>
        <div className={styles.familyCard}>
          <img src={mascot} alt="" />
          <div>
            <strong>{model.familyName}</strong>
            <span>{model.memberCount}</span>
          </div>
        </div>
        <label className={styles.field}>
          <span>내 이름</span>
          <div className={styles.input}>{model.myName}</div>
        </label>
        <div className={styles.field}>
          <span>역할</span>
          <div className={styles.roles}>
            {model.roles.map((role) => (
              <span key={role.label} className={role.selected ? styles.roleOn : styles.role}>{role.label}</span>
            ))}
          </div>
        </div>
        <div className={styles.notice}>
          <i>🛡</i>
          <span>{model.notice}</span>
        </div>
        <button type="button" className={styles.join} onClick={onAccept}>가족 참여하기</button>
        <button type="button" className={styles.decline} onClick={onDecline}>초대를 거절할게요</button>
      </div>
    </main>
  );
}
