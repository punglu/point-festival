import { useState } from 'react';
import styles from '../UserDashboard.module.css';
import { FeedbackResponse } from '../api/dashboardApi';

interface Props {
  feedbacks: FeedbackResponse[];
  sendFeedback: (msg: string) => Promise<void>;
  playerName: string;
}

export default function FeedbackSection({ feedbacks, sendFeedback, playerName }: Props) {
  const [msg, setMsg] = useState('');
  const [sending, setSending] = useState(false);

  const handleSend = async () => {
    if (!msg.trim()) return;
    setSending(true);
    try {
      await sendFeedback(msg.trim());
      setMsg('');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className={styles.feedbackCard}>
      <div className={styles.feedbackTitle}>💬 답장 & 피드백</div>

      {feedbacks.length === 0 ? (
        <div className={styles.emptyMsg}>아직 답장이 없습니다.</div>
      ) : (
        feedbacks.map(fb => (
          <div key={fb.id} style={{ marginBottom: 12 }}>
            <div className={styles.feedbackMsg}>{fb.msg}</div>
            {fb.replies.map(r => (
              <div
                key={r.id}
                className={`${styles.feedbackReply} ${r.sender === '아빠' ? styles.replyDad : styles.replyMom}`}
              >
                <strong>{r.sender}: </strong>{r.text}
              </div>
            ))}
          </div>
        ))
      )}

      <div className={styles.feedbackInputRow}>
        <input
          className={styles.feedbackInput}
          placeholder={`${playerName}의 답장 보내기`}
          value={msg}
          onChange={e => setMsg(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          maxLength={500}
        />
        <button
          className={styles.feedbackSend}
          onClick={handleSend}
          disabled={sending}
        >
          전송
        </button>
      </div>
    </div>
  );
}
