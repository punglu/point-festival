import styles from './UnreadDivider.module.css';

export interface UnreadDividerProps {
  label?: string;
}

export default function UnreadDivider({ label = '여기부터 안 읽음' }: UnreadDividerProps) {
  return (
    <div className={styles.divider} role="separator" aria-label={label}>
      <span className={styles.line} aria-hidden="true" />
      <span className={styles.text}>{label}</span>
      <span className={styles.line} aria-hidden="true" />
    </div>
  );
}
