import { type ButtonHTMLAttributes, type HTMLAttributes } from 'react';
import styles from './Card.module.css';

export type CardVariant = 'section' | 'interactive' | 'metric' | 'hero';

interface CardCommonProps {
  variant?: CardVariant;
  className?: string;
}

export type CardDivProps = CardCommonProps &
  Omit<HTMLAttributes<HTMLDivElement>, 'className'> & { as?: 'div' };

export type CardButtonProps = CardCommonProps &
  Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className'> & { as: 'button' };

export type CardProps = CardDivProps | CardButtonProps;

const variantClass: Record<CardVariant, string> = {
  section: styles.section,
  interactive: styles.interactive,
  metric: styles.metric,
  hero: styles.hero,
};

export default function Card(props: CardProps) {
  const { variant = 'section', className, as, ...rest } = props;
  const cls = [styles.card, variantClass[variant], className].filter(Boolean).join(' ');

  if (as === 'button') {
    const { type = 'button', ...buttonRest } = rest as ButtonHTMLAttributes<HTMLButtonElement>;
    return <button type={type} className={cls} {...buttonRest} />;
  }

  return <div className={cls} {...(rest as HTMLAttributes<HTMLDivElement>)} />;
}
