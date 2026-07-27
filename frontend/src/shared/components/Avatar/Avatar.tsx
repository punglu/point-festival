import styles from './Avatar.module.css';

export type AvatarSize = 28 | 36 | 44 | 56 | 72;
export type AvatarStatus = 'online' | 'offline' | 'locked';

export interface AvatarProps {
  src?: string;
  alt: string;
  fallback: string;
  size?: AvatarSize;
  status?: AvatarStatus;
  className?: string;
}

const statusLabel: Record<AvatarStatus, string> = {
  online: '온라인',
  offline: '오프라인',
  locked: '잠김',
};

const statusClass: Record<AvatarStatus, string> = {
  online: styles.statusOnline,
  offline: styles.statusOffline,
  locked: styles.statusLocked,
};

export default function Avatar({ src, alt, fallback, size = 44, status, className }: AvatarProps) {
  const cls = [styles.avatar, className].filter(Boolean).join(' ');

  return (
    <span className={cls} style={{ width: size, height: size }}>
      {src ? (
        <img className={styles.image} src={src} alt={alt} width={size} height={size} />
      ) : (
        <span className={styles.fallback} style={{ fontSize: size * 0.4 }} role="img" aria-label={alt}>
          {fallback}
        </span>
      )}
      {status && (
        <>
          <span className={`${styles.statusDot} ${statusClass[status]}`} aria-hidden="true" />
          <span className={styles.srOnly}>{statusLabel[status]}</span>
        </>
      )}
    </span>
  );
}
