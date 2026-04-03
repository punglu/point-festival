import styles from '../Auth.module.css';

interface Props {
  name: string;
  photo: string | null;
  level: number | null;
  isLocked: boolean;
  isAlt?: boolean;
  onClick: () => void;
}

export default function PlayerCard({ name, photo, level, isLocked, isAlt, onClick }: Props) {
  return (
    <button className={styles.playerCard} onClick={onClick} disabled={isLocked}>
      <div className={`${styles.playerAvatar} ${isAlt ? styles.playerAvatarAlt : ''}`}>
        {photo ? (
          <img src={photo} alt={name} className={styles.playerPhoto} />
        ) : (
          <span className={styles.playerInitial}>{name.charAt(0)}</span>
        )}
      </div>
      <div className={styles.playerCardBody}>
        <div className={styles.playerName}>{name}</div>
        {level !== null && (
          <div className={styles.playerLevel}>Lv.{level}</div>
        )}
        {isLocked && <div className={styles.lockIcon}>🔒 잠김</div>}
      </div>
      {level !== null && !isLocked && (
        <span className={`${styles.playerPointBadge} ${isAlt ? styles.playerPointBadgeAlt : styles.playerPointBadgeDefault}`}>
          Lv.{level}
        </span>
      )}
    </button>
  );
}
