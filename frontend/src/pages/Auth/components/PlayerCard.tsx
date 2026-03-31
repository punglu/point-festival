import styles from '../Auth.module.css';

interface Props {
  name: string;
  photo: string | null;
  level: number | null;
  isLocked: boolean;
  onClick: () => void;
}

export default function PlayerCard({ name, photo, level, isLocked, onClick }: Props) {
  return (
    <button className={styles.playerCard} onClick={onClick} disabled={isLocked}>
      <div className={styles.playerAvatar}>
        {photo ? (
          <img src={photo} alt={name} className={styles.playerPhoto} />
        ) : (
          <span className={styles.playerInitial}>{name.charAt(0)}</span>
        )}
      </div>
      <span className={styles.playerName}>{name}</span>
      {level !== null && <span className={styles.levelBadge}>Lv.{level}</span>}
      {isLocked && <span className={styles.lockIcon}>🔒</span>}
    </button>
  );
}
