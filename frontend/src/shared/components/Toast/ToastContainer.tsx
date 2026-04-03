import { useToastStore } from '../../stores/useToastStore';
import styles from './ToastContainer.module.css';

const ICON: Record<string, string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
};

export default function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  if (toasts.length === 0) return null;

  return (
    <div className={styles.container}>
      {toasts.map((t) => (
        <div key={t.id} className={`${styles.toast} ${styles[t.type]}`}>
          <span className={styles.icon}>{ICON[t.type]}</span>
          <span className={styles.message}>{t.message}</span>
          <button
            className={styles.close}
            onClick={() => removeToast(t.id)}
            aria-label="닫기"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
