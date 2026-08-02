import styles from './ChatReplyScreen.module.css';
import type { ChatReplyProps } from './types';

export function ChatReplyScreen({
  model,
  onReply,
  onReact,
  onCopy,
  onReport,
  onCancelQuote,
  onSend,
}: ChatReplyProps) {
  const quotedLines = model.quotedText.split('\n');
  return (
    <main className={styles.page} data-canonical-screen-id="2g">
      <div className={styles.dimmed}>
        <div className={styles.status}>
          <span>9:41</span>
        </div>
        <div className={styles.roomTitle}>
          <span>{model.roomTitle}</span>
        </div>
        <div className={styles.thread}>
          {model.backgroundMessages.map((message, index) => (
            <div
              key={index}
              className={message.tone === 'in' ? styles.bubbleIn : styles.bubbleOut}
            >
              {message.text}
            </div>
          ))}
        </div>
      </div>
      <div className={styles.overlay}>
        <div className={styles.quoted}>
          {quotedLines.map((line, index) => (
            <span key={index}>
              {line}
              {index < quotedLines.length - 1 && <br />}
            </span>
          ))}
        </div>
        <div className={styles.menu}>
          <button type="button" onClick={onReply}>
            <span>↩</span>
            <span>답장하기</span>
          </button>
          <button type="button" onClick={onReact}>
            <span>😊</span>
            <span>이모지 반응</span>
          </button>
          <button type="button" onClick={onCopy}>
            <span>📋</span>
            <span>복사하기</span>
          </button>
          <button type="button" className={styles.danger} onClick={onReport}>
            <span>🚫</span>
            <span>신고하기</span>
          </button>
        </div>
      </div>
      <div className={styles.footer}>
        <div className={styles.replyBar}>
          <div className={styles.replyText}>
            <span>{model.quotedAuthor}에게 답장</span>
            <span>{model.backgroundMessages[0]?.text ?? model.quotedText}</span>
          </div>
          <span
            className={styles.cancel}
            role="button"
            tabIndex={0}
            onClick={onCancelQuote}
            aria-label="답장 취소"
          >
            ✕
          </span>
        </div>
        <div className={styles.inputBar}>
          <span className={styles.attach}>📎</span>
          <span className={styles.inputText}>{model.draftText}</span>
          <span
            className={styles.send}
            role="button"
            tabIndex={0}
            onClick={onSend}
            aria-label="전송"
          >
            ➤
          </span>
        </div>
      </div>
    </main>
  );
}
