import { useState, useEffect, useCallback } from 'react';
import styles from './FeedbackView.module.css';
import { adminApi } from '../../api/adminApi';
import { useAdminAuth } from '../../hooks/useAdminAuth';
import PlayerTab from '../../components/PlayerTab/PlayerTab';
import type { Player, FeedbackItem } from '../../types/admin.types';

const TODAY = new Date().toISOString().slice(0, 10);

/* ── 아바타 ── */
function Avatar({ name, isMe }: { name: string; isMe: boolean }) {
  return (
    <div className={isMe ? styles.avatarMe : styles.avatarOther}>
      {name.charAt(0).toUpperCase()}
    </div>
  );
}

/* ── 답장 입력 ── */
function ReplyBox({
  feedbackId,
  senderName,
  onSend,
}: {
  feedbackId: number;
  senderName: string;
  onSend: (feedbackId: number, text: string) => Promise<void>;
}) {
  const [text, setText] = useState('');
  const [sending, setSending] = useState(false);
  const [open, setOpen] = useState(false);

  const handleSend = async () => {
    if (!text.trim()) return;
    setSending(true);
    try {
      await onSend(feedbackId, text.trim());
      setText('');
      setOpen(false);
    } finally {
      setSending(false);
    }
  };

  if (!open) {
    return (
      <button className={styles.replyToggle} onClick={() => setOpen(true)}>
        ↩ 답장 ({senderName})
      </button>
    );
  }

  return (
    <div className={styles.replyInputWrap}>
      <span className={styles.replyAs}>{senderName} 으로 답장:</span>
      <div className={styles.replyInputRow}>
        <input
          className={styles.replyInput}
          placeholder="답장 내용을 입력하세요"
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          maxLength={500}
          autoFocus
        />
        <button className={styles.btnSend} onClick={handleSend} disabled={sending}>전송</button>
        <button className={styles.btnCancel} onClick={() => { setText(''); setOpen(false); }}>취소</button>
      </div>
    </div>
  );
}

/* ── 메인 뷰 ── */
export default function FeedbackView() {
  const { adminDisplayName } = useAdminAuth();
  const senderName = adminDisplayName ?? '관리자';

  const [players,  setPlayers]  = useState<Player[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [date,     setDate]     = useState(TODAY);
  const [feedbacks, setFeedbacks] = useState<FeedbackItem[]>([]);
  const [loading,  setLoading]  = useState(false);

  /* 플레이어 목록 */
  useEffect(() => {
    const ctrl = new AbortController();
    adminApi.getPlayers(ctrl.signal)
      .then(r => setPlayers(r.data.filter(p => p.role === 'player')))
      .catch(() => {});
    return () => ctrl.abort();
  }, []);

  /* 피드백 로드 */
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await adminApi.getFeedbacks(date, selected ?? undefined);
      setFeedbacks(r.data);
    } catch { /* silent */ } finally {
      setLoading(false);
    }
  }, [date, selected]);

  useEffect(() => { load(); }, [load]);

  /* 답장 전송 */
  const handleReply = async (feedbackId: number, text: string) => {
    await adminApi.sendAdminReply({ feedback_id: feedbackId, sender: senderName, text });
    await load();
  };

  /* 날짜 이동 */
  const moveDate = (delta: number) => {
    const d = new Date(date);
    d.setDate(d.getDate() + delta);
    setDate(d.toISOString().slice(0, 10));
  };

  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <h1 className={styles.title}>💬 가족 채팅</h1>
        <span className={styles.senderBadge}>{senderName} 으로 답장</span>
      </div>

      {/* 날짜 선택 */}
      <div className={styles.dateRow}>
        <button className={styles.dateBtn} onClick={() => moveDate(-1)}>◀</button>
        <input
          type="date"
          className={styles.dateInput}
          value={date}
          onChange={e => setDate(e.target.value)}
        />
        <button className={styles.dateBtn} onClick={() => moveDate(1)}>▶</button>
      </div>

      {/* 플레이어 탭 */}
      <PlayerTab players={players} selected={selected} onSelect={setSelected} />

      {/* 채팅 목록 */}
      <div className={styles.chatArea}>
        {loading ? (
          <div className={styles.empty}>로딩 중...</div>
        ) : feedbacks.length === 0 ? (
          <div className={styles.empty}>이 날짜에 메세지가 없습니다.</div>
        ) : (
          feedbacks.map(fb => {
            const playerName = fb.player_name ?? `플레이어 ${fb.player_id}`;
            return (
              <div key={fb.id} className={styles.thread}>
                {/* 플레이어 메세지 — 좌측 */}
                <div className={styles.rowLeft}>
                  <Avatar name={playerName} isMe={false} />
                  <div className={styles.bubblePlayer}>
                    <span className={styles.bubbleSender}>{playerName}</span>
                    <p className={styles.bubbleText}>{fb.msg}</p>
                  </div>
                </div>

                {/* 답글 */}
                {fb.replies.map(r => {
                  const isMe = r.sender === senderName;
                  return (
                    <div key={r.id} className={isMe ? styles.rowRight : styles.rowLeft}>
                      {!isMe && <Avatar name={r.sender} isMe={false} />}
                      <div className={isMe ? styles.bubbleMe : styles.bubbleOther}>
                        <span className={styles.bubbleSender}>{r.sender}</span>
                        <p className={styles.bubbleText}>{r.text}</p>
                      </div>
                      {isMe && <Avatar name={r.sender} isMe />}
                    </div>
                  );
                })}

                {/* 관리자 답장 입력 */}
                <ReplyBox feedbackId={fb.id} senderName={senderName} onSend={handleReply} />
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
