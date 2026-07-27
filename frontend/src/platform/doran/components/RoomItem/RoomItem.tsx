import styles from './RoomItem.module.css';

export type RoomKind = 'DIRECT' | 'GROUP' | 'SERVICE';

export interface RoomItemProps {
  kind: RoomKind;
  title: string;
  preview?: string;
  activityLabel?: string;
  unreadCount?: number;
  selected?: boolean;
  onSelect?: () => void;
}

const kindLabel: Record<RoomKind, string> = {
  DIRECT: '개인 대화',
  GROUP: '가족 그룹',
  SERVICE: '서비스 알림',
};

export default function RoomItem({
  kind,
  title,
  preview,
  activityLabel,
  unreadCount,
  selected = false,
  onSelect,
}: RoomItemProps) {
  const unreadDisplay =
    typeof unreadCount === 'number' && unreadCount > 0
      ? { display: unreadCount > 99 ? '99+' : String(unreadCount), count: unreadCount }
      : null;

  return (
    <button
      type="button"
      className={[styles.roomItem, selected ? styles.selected : ''].filter(Boolean).join(' ')}
      onClick={onSelect}
      aria-current={selected ? 'true' : undefined}
    >
      <span className={styles.kindTag} data-kind={kind}>
        {kindLabel[kind]}
      </span>
      <span className={styles.meta}>
        <strong className={styles.title}>{title}</strong>
        {preview && <span className={styles.preview}>{preview}</span>}
      </span>
      <span className={styles.activity}>
        {activityLabel && <span className={styles.activityLabel}>{activityLabel}</span>}
        {unreadDisplay && (
          <span className={styles.unreadBadge}>
            <span aria-hidden="true">{unreadDisplay.display}</span>
            <span className={styles.srOnly}>안 읽은 메시지 {unreadDisplay.count}개</span>
          </span>
        )}
      </span>
    </button>
  );
}
