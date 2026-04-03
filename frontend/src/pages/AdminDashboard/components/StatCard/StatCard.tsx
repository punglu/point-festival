import styles from './StatCard.module.css';

interface StatCardProps {
  label: string;
  value: number | string;
  subtext?: string;
  subtextColor?: string;
  onClick?: () => void;
}

export default function StatCard({ label, value, subtext, subtextColor, onClick }: StatCardProps) {
  return (
    <div
      className={`${styles.card} ${onClick ? styles.clickable : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className={styles.label}>{label}</div>
      <div className={styles.value}>{value}</div>
      {subtext && (
        <div className={styles.subtext} style={subtextColor ? { color: subtextColor } : undefined}>
          {subtext}
        </div>
      )}
    </div>
  );
}
