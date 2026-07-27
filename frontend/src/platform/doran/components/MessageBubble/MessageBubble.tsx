import { type ReactNode } from 'react';
import { Avatar } from '../../../../shared/components/Avatar';
import styles from './MessageBubble.module.css';

export type MessageDirection = 'incoming' | 'outgoing';
export type MessageReadState = 'sending' | 'sent' | 'read' | 'failed';
export type MessageGrouped = 'first' | 'middle' | 'last' | 'single';

export interface MessageBubbleSender {
  name: string;
  avatar?: string;
}

export interface MessageBubbleProps {
  direction: MessageDirection;
  sender?: MessageBubbleSender;
  timestamp: string;
  readState?: MessageReadState;
  grouped?: MessageGrouped;
  children: ReactNode;
}

const readStateLabel: Record<MessageReadState, string> = {
  sending: '전송 중',
  sent: '전송됨',
  read: '읽음',
  failed: '전송 실패',
};

export default function MessageBubble({
  direction,
  sender,
  timestamp,
  readState,
  grouped = 'single',
  children,
}: MessageBubbleProps) {
  const showSenderIdentity = direction === 'incoming' && sender && (grouped === 'first' || grouped === 'single');

  return (
    <div
      className={[
        styles.row,
        direction === 'incoming' ? styles.incoming : styles.outgoing,
        styles[`grouped-${grouped}`],
      ].join(' ')}
    >
      {direction === 'incoming' && (
        <span className={styles.avatarSlot}>
          {showSenderIdentity && sender && (
            <Avatar src={sender.avatar} alt={sender.name} fallback={sender.name.charAt(0)} size={28} />
          )}
        </span>
      )}
      <div className={styles.content}>
        {showSenderIdentity && sender && <span className={styles.senderName}>{sender.name}</span>}
        <div className={[styles.bubble, readState === 'failed' ? styles.failed : ''].join(' ')}>{children}</div>
        <div className={styles.footer}>
          <span className={styles.timestamp}>{timestamp}</span>
          {readState && (
            <>
              <span className={styles.readStateText} aria-hidden="true">
                {readState === 'read' ? '읽음' : readState === 'sent' ? '전송됨' : readState === 'sending' ? '전송 중' : '실패'}
              </span>
              <span className={styles.srOnly}>{readStateLabel[readState]}</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
