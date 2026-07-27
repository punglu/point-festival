import { type ButtonHTMLAttributes, type ReactNode } from 'react';
import styles from './IconButton.module.css';

export type IconButtonTone = 'neutral' | 'brand' | 'danger';

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  label: string;
  icon: ReactNode;
  tone?: IconButtonTone;
  badgeCount?: number;
}

const toneClass: Record<IconButtonTone, string> = {
  neutral: styles.toneNeutral,
  brand: styles.toneBrand,
  danger: styles.toneDanger,
};

export default function IconButton({
  label,
  icon,
  tone = 'neutral',
  badgeCount,
  type = 'button',
  className,
  disabled,
  ...rest
}: IconButtonProps) {
  const cls = [styles.iconButton, toneClass[tone], className].filter(Boolean).join(' ');
  const displayBadge = typeof badgeCount === 'number' && badgeCount > 0
    ? (badgeCount > 99 ? '99+' : String(badgeCount))
    : null;

  return (
    <button type={type} className={cls} aria-label={label} disabled={disabled} {...rest}>
      <span className={styles.iconSlot} aria-hidden="true">
        {icon}
      </span>
      {displayBadge && (
        <span className={styles.badge} aria-hidden="true">
          {displayBadge}
        </span>
      )}
    </button>
  );
}
