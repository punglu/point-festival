import styles from './ProfileSelectorScreen.module.css';
import type { ProfileSelectorScreenProps } from './types';

export function ProfileSelectorScreen({ model, onSelect }: ProfileSelectorScreenProps) {
  return <main className={styles.screen} data-canonical-screen-id="1a" data-canonical-screen-label="로그인" data-canonical-source="wave7-full-authority">
    <section className={styles.heading}><h1>{model.title}</h1><p>{model.subtitle}</p></section>
    <section className={styles.profiles}>{model.profiles.map((profile) => <button className={styles.profile} type="button" key={profile.name} onClick={() => onSelect?.(profile.name)}><i className={styles.avatar}>{profile.initial}</i><span><strong>{profile.name}</strong><span>{profile.role}</span></span></button>)}</section>
  </main>;
}
