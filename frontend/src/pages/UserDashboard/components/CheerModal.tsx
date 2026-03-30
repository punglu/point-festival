import styles from '../UserDashboard.module.css';

interface Props {
  sender: string;
  message: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function CheerModal({ sender, message, isOpen, onClose }: Props) {
  if (!isOpen) return null;

  const emoji = sender === '아빠' || sender === 'dad' ? '👨' : '👩';

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalBox} onClick={e => e.stopPropagation()}>
        <div className={styles.modalTitle}>
          {emoji} {sender}의 응원
        </div>
        <p style={{ fontSize: 15, lineHeight: 1.7, color: 'var(--text-primary, #f1f5f9)' }}>
          {message}
        </p>
        <button className={styles.modalClose} onClick={onClose}>닫기</button>
      </div>
    </div>
  );
}
