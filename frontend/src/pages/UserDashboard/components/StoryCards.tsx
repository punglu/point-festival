import styles from '../UserDashboard.module.css';

export interface SenderConfig {
  key: string;
  label: string;
  color: string;
  emoji: string;
}

interface Props {
  cheers: Record<string, string>;
  parentPhotos: Record<string, string>;
  senders: SenderConfig[];
}

const DEFAULT_CHEER = '오늘도 화이팅!';

export default function StoryCards({ cheers, parentPhotos, senders }: Props) {
  return (
    <div className={styles.cheerSection}>
      <div className={styles.cheerGrid}>
        {senders.map((sender) => (
          <div key={sender.key} className={styles.cheerItem}>
            <div className={styles.cheerPhotoRing} style={{ borderColor: sender.color }}>
              {parentPhotos[sender.key] ? (
                <img src={parentPhotos[sender.key]} alt={sender.label} className={styles.cheerPhoto} />
              ) : (
                <span className={styles.cheerInitial}>{sender.label}</span>
              )}
            </div>
            <div className={styles.cheerBubbleWrapper}>
              <span className={styles.cheerLabel} style={{ color: sender.color }}>{sender.label}</span>
              <div className={styles.cheerBubble}>
                {cheers[sender.key] || DEFAULT_CHEER}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
