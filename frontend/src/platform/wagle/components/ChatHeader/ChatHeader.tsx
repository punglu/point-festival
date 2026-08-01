import { type ReactNode } from 'react';
import { Avatar } from '../../../../shared/components/Avatar';
import { IconButton } from '../../../../shared/components/IconButton';
import { BackIcon } from '../../../../shared/components/icons/outline';
import styles from './ChatHeader.module.css';

export interface ChatHeaderParticipant {
  id: string;
  name: string;
  avatarSrc?: string;
  avatarFallback: string;
}

export interface ChatHeaderProps {
  roomName: string;
  participantSummary?: string;
  participants?: ChatHeaderParticipant[];
  connectionLabel?: string;
  onBack: () => void;
  backLabel?: string;
  actions?: ReactNode;
}

const MAX_VISIBLE_PARTICIPANTS = 4;

export default function ChatHeader({
  roomName,
  participantSummary,
  participants,
  connectionLabel,
  onBack,
  backLabel = '뒤로가기',
  actions,
}: ChatHeaderProps) {
  const visible = participants?.slice(0, MAX_VISIBLE_PARTICIPANTS) ?? [];
  const overflow = participants ? Math.max(0, participants.length - MAX_VISIBLE_PARTICIPANTS) : 0;

  return (
    <header className={styles.header}>
      <IconButton label={backLabel} icon={<BackIcon size={20} />} onClick={onBack} className={styles.backButton} />
      <div className={styles.identity}>
        <h2 className={styles.roomName}>{roomName}</h2>
        {participantSummary && <p className={styles.participantSummary}>{participantSummary}</p>}
      </div>
      {visible.length > 0 && (
        <div className={styles.avatarStack} aria-hidden="true">
          {visible.map((participant) => (
            <Avatar
              key={participant.id}
              src={participant.avatarSrc}
              alt={participant.name}
              fallback={participant.avatarFallback}
              size={28}
              className={styles.stackedAvatar}
            />
          ))}
          {overflow > 0 && <span className={styles.overflowBadge}>+{overflow}</span>}
        </div>
      )}
      {connectionLabel && <span className={styles.connectionLabel}>{connectionLabel}</span>}
      {actions && <div className={styles.actions}>{actions}</div>}
    </header>
  );
}
