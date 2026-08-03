import { useState } from 'react';
import styles from './AdminNotificationSendScreen.module.css';
import type { AdminNotificationSendProps } from './types';
export function AdminNotificationSendScreen({ model, onSend, onCancel }: AdminNotificationSendProps) {
  const [subject, setSubject] = useState(model.subject);
  const [message, setMessage] = useState(model.message);
  return (
    <main className={styles.screen} data-canonical-screen-id="2t" data-canonical-screen-label="관리자 알림 발송" data-canonical-source="wave7-full-authority">
      <section className={styles.dialog}>
        <header><div><span>알림 관리</span><h1>{model.title}</h1></div><button type="button" onClick={onCancel}>×</button></header>
        <p>가족에게 전달할 알림 내용을 작성해 주세요.</p>
        <form onSubmit={(e) => { e.preventDefault(); onSend?.({ subject, message }); }}>
          <label>받는 대상<select defaultValue={model.recipients}><option>{model.recipients}</option></select></label>
          <label>제목<input value={subject} onChange={(e) => setSubject(e.target.value)} /></label>
          <label>내용<textarea value={message} onChange={(e) => setMessage(e.target.value)} /></label>
          {model.errorMessage && <div className={styles.error}>{model.errorMessage}</div>}
          <aside><b>발송 전 확인</b><span>알림은 선택한 가족 구성원에게 즉시 전달됩니다.</span></aside>
          <div className={styles.actions}>
            <button type="button" onClick={onCancel}>취소</button>
            <button type="submit" disabled={model.isSending}>{model.isSending ? '발송 중…' : '알림 발송'}</button>
          </div>
        </form>
      </section>
    </main>
  );
}
