import styles from './PlayerBadge.module.css';

const GRADIENTS = [
  'linear-gradient(135deg, #4338CA, #818CF8)',
  'linear-gradient(135deg, #DB2777, #F472B6)',
  'linear-gradient(135deg, #059669, #34D399)',
  'linear-gradient(135deg, #D97706, #FCD34D)',
];

interface PlayerBadgeProps {
  name: string;
  index?: number;
  size?: 'sm' | 'md' | 'lg';
  photo?: string | null;
}

export default function PlayerBadge({ name, index = 0, size = 'md', photo }: PlayerBadgeProps) {
  const gradient = GRADIENTS[index % GRADIENTS.length];
  const sizeClass = styles[size];

  if (photo) {
    return (
      <img
        src={photo}
        alt={name}
        className={`${styles.badge} ${sizeClass} ${styles.badgeImg}`}
      />
    );
  }

  return (
    <div
      className={`${styles.badge} ${sizeClass}`}
      style={{ background: gradient }}
    >
      {name.charAt(0)}
    </div>
  );
}
