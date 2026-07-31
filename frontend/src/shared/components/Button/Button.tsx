import { ButtonHTMLAttributes } from 'react';
import styles from './Button.module.css';

type ButtonVariant = 'primary' | 'ghost' | 'dangerSm';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

const variantMap: Record<ButtonVariant, string> = {
  primary: styles.primary,
  ghost: styles.ghost,
  dangerSm: styles.dangerSm,
};

export default function Button({
  variant = 'primary',
  className,
  children,
  type = 'button',
  ...props
}: ButtonProps) {
  const cls = [variantMap[variant], className].filter(Boolean).join(' ');
  return (
    <button type={type} className={cls} {...props}>
      {children}
    </button>
  );
}
