import { useEffect, useRef } from 'react';

import mascot from '../../../assets/logos/family-platform-mascot.png';

import styles from './FamilyChatScreen.module.css';
import type { FamilyChatMessage, FamilyChatProps } from './types';

const TONE_COUNT = 4;

function Avatar({ name, index }: { name: string; index: number }) {
  return (
    <span className={`${styles.avatar} ${styles[`tone${index % TONE_COUNT}`]}`}>
      {name.charAt(0)}
    </span>
  );
}

function MessageRow({
  message,
  toneIndex,
  onReplyMessage,
}: {
  message: FamilyChatMessage;
  toneIndex: number;
  onReplyMessage?: (messageId: string) => void;
}) {
  if (message.kind === 'service') {
    return (
      <li className={styles.serviceRow} data-message-id={message.id} data-actor="service">
        <div className={styles.serviceCard}>
          <span className={styles.serviceBadge}>{message.serviceBadge ?? '서비스'}</span>
          <span>{message.deleted ? message.tombstone : (message.body ?? '서비스 알림')}</span>
        </div>
      </li>
    );
  }

  const isOwn = message.kind === 'own';
  return (
    <li
      className={`${styles.messageRow} ${isOwn ? styles.own : ''}`}
      data-message-id={message.id}
      data-actor={isOwn ? 'self' : 'other'}
    >
      {!isOwn && <Avatar name={message.authorName ?? '가족'} index={toneIndex} />}
      <div className={styles.bubbleCol}>
        {!isOwn && <b className={styles.author}>{message.authorName}</b>}
        <div className={styles.bubbleLine}>
          {message.replyPreview && !message.deleted && (
            <span className={styles.replyQuote} data-testid={`wagle-reply-quote-${message.id}`}>
              ↩ {message.replyPreview}
            </span>
          )}
          {message.deleted ? (
            <p className={`${styles.bubble} ${styles.tombstone}`}>{message.tombstone ?? '삭제된 메시지'}</p>
          ) : (
            <p className={styles.bubble}>{message.body}</p>
          )}
          <time className={styles.time}>{message.time}</time>
        </div>
        {!message.deleted && (
          <button
            type="button"
            className={styles.replyTrigger}
            onClick={() => onReplyMessage?.(message.id)}
            aria-label="답장하기"
            data-testid={`wagle-reply-${message.id}`}
          >
            ↩
          </button>
        )}
      </div>
    </li>
  );
}

export function FamilyChatScreen({
  model,
  onBack,
  onDraftChange,
  onSend,
  onReplyMessage,
  onCancelReply,
  onOpenSettings,
  onOpenFiles,
}: FamilyChatProps) {
  const canSend = !model.sending && model.draft.trim() !== '';
  const listEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    listEndRef.current?.scrollIntoView({ block: 'end' });
  }, [model.messages]);

  const toneIndexByName = new Map(model.participants.map((p, index) => [p.name, index]));

  return (
    <main className={styles.page} data-canonical-screen-id="1d">
      <header className={styles.header}>
        <button type="button" className={styles.back} onClick={onBack} aria-label="뒤로">
          ←
        </button>
        <div className={styles.roomTitle}>
          <strong>{model.roomTitle}</strong>
          <span data-testid="wagle-connection-state" data-state={model.connectionState}>
            <i />
            {model.connectionLabel}
          </span>
        </div>
        <div className={styles.participants}>
          {model.participants.slice(0, TONE_COUNT).map((participant, index) => (
            <Avatar key={participant.id} name={participant.name} index={index} />
          ))}
        </div>
        <div className={styles.headerActions}>
          <button type="button" onClick={onOpenFiles} aria-label="사진/파일" data-testid="wagle-open-files">
            🖼
          </button>
          <button type="button" onClick={onOpenSettings} aria-label="채팅방 설정" data-testid="wagle-open-settings">
            ⚙
          </button>
        </div>
        <div className={styles.mascot}>
          <img src={mascot} alt="" />
          <i />
        </div>
      </header>

      {model.messages.length === 0 ? (
        <p className={styles.empty} data-testid="wagle-messages-empty">
          아직 메시지가 없어요.
        </p>
      ) : (
        <ol className={styles.thread} aria-label="가족 대화" data-testid="wagle-messages">
          {model.messages.map((message) => (
            <MessageRow
              key={message.id}
              message={message}
              toneIndex={message.authorName ? (toneIndexByName.get(message.authorName) ?? 0) : 0}
              onReplyMessage={onReplyMessage}
            />
          ))}
        </ol>
      )}
      <div ref={listEndRef} />


      {model.replyBannerText && (
        <div className={styles.replyBanner} data-testid="wagle-reply-banner">
          <span className={styles.replyBannerText}>답장: {model.replyBannerText}</span>
          <button type="button" onClick={onCancelReply} aria-label="답장 취소" data-testid="wagle-reply-cancel">
            ✕
          </button>
        </div>
      )}

      <div className={styles.composer}>
        <label className={styles.srOnly} htmlFor="wagle-draft">
          메시지 입력
        </label>
        <input
          id="wagle-draft"
          className={styles.input}
          value={model.draft}
          disabled={model.sending}
          onChange={(event) => onDraftChange?.(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault();
              if (canSend) onSend?.();
            }
          }}
          placeholder="메시지를 입력하세요"
          data-testid="wagle-composer-input"
        />
        <button
          type="button"
          className={styles.send}
          disabled={!canSend}
          onClick={() => onSend?.()}
          data-testid="wagle-send"
        >
          {model.sending ? '전송 중…' : '보내기'}
        </button>
      </div>
      {model.sendError && (
        <p className={styles.error} role="alert">
          {model.sendError}
        </p>
      )}
    </main>
  );
}
