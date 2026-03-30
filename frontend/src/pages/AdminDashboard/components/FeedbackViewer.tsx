import { useState, useEffect } from 'react';
import styles from '../AdminDashboard.module.css';
import { adminApi, FeedbackItem } from '../api/adminApi';

interface Props {
  playerId: number | null;
  selectedDate: string;
}

export default function FeedbackViewer({ playerId, selectedDate }: Props) {
  const [feedbacks, setFeedbacks] = useState<FeedbackItem[]>([]);
  const [replyText, setReplyText] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const abortController = new AbortController();
    if (!playerId) return;
    adminApi.getFeedbacks(playerId, selectedDate, abortController.signal)
      .then((res) => { if (!abortController.signal.aborted) setFeedbacks(res.data); })
      .catch(() => {});
    return () => abortController.abort();
  }, [playerId, selectedDate]);

  const handleReply = async (feedbackId: number) => {
    const text = replyText[feedbackId]?.trim();
    if (!text) return;
    setLoading(true);
    try {
      await adminApi.createReply(feedbackId, { feedback_id: feedbackId, sender: '관리자', text });
      setReplyText((prev) => ({ ...prev, [feedbackId]: '' }));
      if (playerId) {
        const res = await adminApi.getFeedbacks(playerId, selectedDate);
        setFeedbacks(res.data);
      }
    } catch {
      alert('답글 전송 실패');
    } finally {
      setLoading(false);
    }
  };

  if (!playerId) return <div className={styles.adminCard}><div className={styles.emptyMsg}>플레이어를 선택해주세요.</div></div>;

  return (
    <div className={styles.adminCard}>
      <div className={styles.adminCardTitle}>피드백 조회/답글</div>

      {feedbacks.length === 0 ? (
        <div className={styles.emptyMsg}>피드백이 없습니다.</div>
      ) : (
        feedbacks.map((fb) => (
          <div key={fb.id} className={styles.listRow}>
            <div className={styles.listRowBody} style={{ marginBottom: 8 }}>"{fb.msg}"</div>
            {fb.replies.map((r) => (
              <div key={r.id} style={{ paddingLeft: 16, fontSize: 13, color: '#4a5568', marginBottom: 4 }}>
                ↳ {r.sender}: {r.text}
              </div>
            ))}
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <input
                className={styles.formInput}
                style={{ flex: 1 }}
                placeholder="답글 작성..."
                value={replyText[fb.id] ?? ''}
                onChange={(e) => setReplyText((prev) => ({ ...prev, [fb.id]: e.target.value }))}
              />
              <button className={styles.btnPrimary} onClick={() => handleReply(fb.id)} disabled={loading}>전송</button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
