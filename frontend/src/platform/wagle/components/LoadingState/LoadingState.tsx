import styles from './LoadingState.module.css';

export interface LoadingStateProps {
  label?: string;
  minHeight?: number | string;
}

export default function LoadingState({ label = '불러오는 중', minHeight = 120 }: LoadingStateProps) {
  return (
    <div className={styles.state} role="status" aria-busy="true" aria-live="polite" style={{ minHeight }}>
      <span className={styles.skeleton} aria-hidden="true" />
      <span className={styles.skeleton} aria-hidden="true" />
      <span className={styles.label}>{label}</span>
    </div>
  );
}
