import mascot from '../../../assets/logos/family-platform-mascot.png';
import styles from './ProfileSelectorScreen.module.css';
import type { ProfileSelectorScreenProps } from './types';

export function ProfileSelectorScreen({ model, onSelect, onAdminLogin }: ProfileSelectorScreenProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="1a" data-canonical-screen-label="로그인" data-canonical-source="wave7-full-authority">
      <div className={styles.hero}>
        <img className={styles.logo} src={mascot} alt="브랜드 핀 로고" />
        <h2>{model.brand}</h2>
        <p>{model.tagline}</p>
      </div>
      <div className={styles.card}>
        <h3>{model.heading}</h3>
        {model.profiles.map((profile) =>
          profile.locked ? (
            <button className={styles.profileLocked} type="button" key={profile.name} onClick={() => onSelect?.(profile.name)}>
              <span className={styles.avatarWrap}>
                <i className={styles.avatarLocked}>{profile.name.slice(0, 1)}</i>
                <em className={styles.lockBadge}>🔒</em>
              </span>
              <span className={styles.profileInfo}>
                <strong>{profile.name}</strong>
                <span className={styles.lockReason}>🔒 {profile.lockReason}</span>
                <small>{profile.lockRetry}</small>
              </span>
              <i className={styles.chevronMuted}>›</i>
            </button>
          ) : (
            <button className={styles.profile} type="button" key={profile.name} onClick={() => onSelect?.(profile.name)}>
              <span className={styles.avatarWrap}>
                <i className={styles.avatar}>{profile.name.slice(0, 1)}</i>
                <em className={styles.onlineDot} />
              </span>
              <span className={styles.profileInfo}>
                <strong>{profile.name}</strong>
                <span className={styles.levelBadge}>{profile.level}</span>
                <span className={styles.points}><i>★</i>{profile.points}</span>
              </span>
              <i className={styles.chevron}>›</i>
            </button>
          ),
        )}
        {model.lockedNotice && (
          <div className={styles.notice}>
            <span>🛡️</span>
            <div>
              <strong>{model.lockedNotice.title}</strong>
              <small>{model.lockedNotice.body}</small>
            </div>
          </div>
        )}
        <div className={styles.footer}>
          <span className={styles.settings}>⚙</span>
          <button type="button" className={styles.adminLogin} onClick={onAdminLogin}>{model.adminLoginLabel} <b>›</b></button>
        </div>
        <div className={styles.homeBar} />
      </div>
    </main>
  );
}
