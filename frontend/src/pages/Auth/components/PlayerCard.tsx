import styles from '../Auth.module.css';
import { Avatar } from '../../../shared/components/Avatar';
import AppIcon from '../../../shared/components/AppIcon';

interface Props {
  name: string;
  photo: string | null;
  level: number | null;
  totalPoints: number;
  isLocked: boolean;
  onClick: () => void;
}

export default function PlayerCard({ name, photo, level, totalPoints, isLocked, onClick }: Props) {
  return (
    <button className={styles.playerCard} onClick={onClick} disabled={isLocked}>
      <Avatar
        src={photo ?? undefined}
        alt={name}
        fallback={name.charAt(0)}
        size="md"
        status={isLocked ? 'locked' : 'online'}
        className={isLocked ? styles.profileAvatarLocked : undefined}
      />
      <div className={styles.profileCardBody}>
        <div className={styles.profileName}>{name}</div>
        {isLocked ? (
          <div className={styles.profileLockedLabel}>🔒 잠김</div>
        ) : (
          <div className={styles.profileMetaRow}>
            {level !== null && <span className={styles.profileLevel}>Lv.{level}</span>}
            <span className={styles.profilePoints}>
              <AppIcon name="star" size={13} />
              {totalPoints.toLocaleString()}P
            </span>
          </div>
        )}
      </div>
      {!isLocked && (
        <span className={styles.profileChevron} aria-hidden="true">
          ›
        </span>
      )}
    </button>
  );
}
