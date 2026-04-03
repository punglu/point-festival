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
    <div className={styles.cheerRow}>
      {senders.map((sender, idx) => {
        const isDad = idx === 0;
        return (
          <div
            key={sender.key}
            className={`${styles.cheerCard} ${isDad ? styles.cheerCardDad : styles.cheerCardMom}`}
          >
            <div className={`${styles.cheerAvatar} ${isDad ? styles.cheerAvatarDad : styles.cheerAvatarMom}`}>
              {parentPhotos[sender.key] ? (
                <img src={parentPhotos[sender.key]} alt={sender.label} className={styles.cheerPhoto} />
              ) : (
                <span>{sender.emoji || sender.label[0]}</span>
              )}
            </div>
            <div className={`${styles.cheerBubble} ${isDad ? styles.cheerBubbleDad : styles.cheerBubbleMom}`}>
              {cheers[sender.key] || DEFAULT_CHEER}
            </div>
          </div>
        );
      })}
    </div>
  );
}
