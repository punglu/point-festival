import styles from './DateDivider.module.css';

export interface DateDividerProps {
  label: string;
}

export default function DateDivider({ label }: DateDividerProps) {
  return (
    <div className={styles.divider} role="separator" aria-label={label}>
      <span>{label}</span>
    </div>
  );
}
