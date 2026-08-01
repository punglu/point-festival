import { useState, type KeyboardEvent } from 'react';
import { IconButton } from '../../../../shared/components/IconButton';
import { AttachIcon, CameraIcon, SendIcon } from '../../../../shared/components/icons/outline';
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
  // 첨부/카메라는 실제 업로드 백엔드가 없다(PM 설계서 §8.19 PhotoMessage
  // DEFERRED_WITH_REASON). 목업(Z9)은 두 아이콘을 항상 노출하므로 시각적으로는
  // 보여주되, 실제 소비처가 attachmentEnabled+onAttach를 모두 제공하기 전까지는
  // disabled preview로만 두고 클릭해도 아무 것도 호출하지 않는다(Wave 6.0B §7).
  const attachInteractive = attachmentEnabled && Boolean(onAttach) && !disabled && !sending;

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
      <IconButton
        label={attachInteractive ? '파일 첨부' : '파일 첨부 (준비 중)'}
        icon={<AttachIcon size={20} />}
        onClick={attachInteractive ? onAttach : undefined}
        disabled={!attachInteractive}
        className={styles.accessoryButton}
      />
      <IconButton
        label="사진 촬영 (준비 중)"
        icon={<CameraIcon size={20} />}
        disabled
        className={styles.accessoryButton}
      />
      <label className={styles.srOnly} htmlFor="wagle-chat-composer-input">
        메시지
      </label>
      <textarea
        id="wagle-chat-composer-input"
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
        className={styles.sendButton}
      />
    </form>
  );
}
