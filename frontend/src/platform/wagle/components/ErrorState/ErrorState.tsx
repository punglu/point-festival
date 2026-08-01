import styles from './ErrorState.module.css';

export interface ErrorStateProps {
  title: string;
  description?: string;
  retryLabel?: string;
  onRetry?: () => void;
  retryDisabled?: boolean;
}

export default function ErrorState({
  title,
  description,
  retryLabel = '다시 시도',
  onRetry,
  retryDisabled = false,
}: ErrorStateProps) {
  return (
    <div className={styles.state} role="alert">
      <strong className={styles.title}>{title}</strong>
      {description && <p className={styles.description}>{description}</p>}
      {onRetry && (
        <button
          type="button"
          className={styles.retryButton}
          onClick={onRetry}
          disabled={retryDisabled}
          aria-disabled={retryDisabled || undefined}
        >
          {retryLabel}
        </button>
      )}
      {retryDisabled && onRetry && <span className={styles.retryHint}>지금은 다시 시도할 수 없어요</span>}
    </div>
  );
}
