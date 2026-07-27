import { useState, type KeyboardEvent } from 'react';
import { IconButton } from '../../../../shared/components/IconButton';
import { AttachIcon, SendIcon } from '../../../../shared/components/icons/outline';
import styles from './ChatComposer.module.css';

export interface ChatComposerProps {
  value: string;
  disabled?: boolean;
  sending?: boolean;
  attachmentEnabled?: boolean;
  onChange: (value: string) => void;
  onSend: () => void;
  onAttach?: () => void;
}

export default function ChatComposer({
  value,
  disabled = false,
  sending = false,
  attachmentEnabled = false,
  onChange,
  onSend,
  onAttach,
}: ChatComposerProps) {
  const [isComposing, setIsComposing] = useState(false);
  const canSend = !disabled && !sending && value.trim().length > 0;

  const handleSend = () => {
    if (canSend) onSend();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    // IME 조합 중 Enter는 전송이 아니라 조합 확정이므로 제외한다 (중복 전송 방지).
    if (event.key === 'Enter' && !event.shiftKey && !isComposing) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <form
      className={styles.composer}
      aria-label="메시지 입력"
      onSubmit={(event) => {
        event.preventDefault();
        handleSend();
      }}
    >
      {attachmentEnabled && (
        <IconButton
          label="파일 첨부"
          icon={<AttachIcon size={20} />}
          onClick={onAttach}
          disabled={disabled || sending}
        />
      )}
      <label className={styles.srOnly} htmlFor="doran-chat-composer-input">
        메시지
      </label>
      <textarea
        id="doran-chat-composer-input"
        className={styles.input}
        value={value}
        disabled={disabled}
        rows={1}
        placeholder="메시지를 입력하세요"
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        onCompositionStart={() => setIsComposing(true)}
        onCompositionEnd={() => setIsComposing(false)}
      />
      <IconButton
        label={sending ? '전송 중' : '보내기'}
        icon={<SendIcon size={20} />}
        tone="brand"
        type="submit"
        disabled={!canSend}
        aria-busy={sending || undefined}
      />
    </form>
  );
}
