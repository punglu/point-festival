import styles from '../UserDashboard.module.css';

interface Props {
  sender: string;
  emoji: string;
  message: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function CheerModal({ sender, emoji, message, isOpen, onClose }: Props) {
  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalBox} onClick={e => e.stopPropagation()}>
        <div className={styles.modalTitle}>
          {emoji} {sender}의 응원
        </div>
        <p className={styles.modalMessage}>
          {message}
        </p>
        <button className={styles.modalClose} onClick={onClose}>닫기</button>
      </div>
    </div>
  );
}
