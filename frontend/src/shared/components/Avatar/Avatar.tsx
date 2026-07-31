import styles from './Avatar.module.css';

export type AvatarNamedSize = 'xs' | 'sm' | 'md' | 'lg';
/*
 * MONGLE_W6_1: AvatarSize is widened, not replaced — the original numeric union
 * is kept in full for existing consumers (ChatHeader/MessageBubble/RoomItem/
 * DoranLanding all currently pass numeric literals; zero behavior change for
 * them). The named xs/sm/md/lg scale is the tablet-confirmed, canonical-token-
 * backed scale (MONGLE_W6_DESIGN_TOKEN_FREEZE.md "Avatar scale", promoted per
 * Component Boundary Freeze's explicit Wave 6.1 recommendation) offered as an
 * additional, forward-looking option.
 */
export type AvatarSize = 28 | 36 | 44 | 56 | 72 | AvatarNamedSize;
export type AvatarStatus = 'online' | 'offline' | 'locked';

const namedSizePx: Record<AvatarNamedSize, number> = {
  xs: 34,
  sm: 44,
  md: 60,
  lg: 78,
};

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
  const sizePx = typeof size === 'string' ? namedSizePx[size] : size;

  return (
    <span className={cls} style={{ width: sizePx, height: sizePx }}>
      {src ? (
        <img className={styles.image} src={src} alt={alt} width={sizePx} height={sizePx} />
      ) : (
        <span className={styles.fallback} style={{ fontSize: sizePx * 0.4 }} role="img" aria-label={alt}>
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
