import { useState } from 'react';
import styles from '../UserDashboard.module.css';
import { FeedbackResponse, PlayerResponse } from '../api/dashboardApi';
import { SenderConfig } from '../hooks/useDashboard';

interface Props {
  feedbacks:    FeedbackResponse[];
  sendFeedback: (msg: string, recipient: string) => Promise<void>;
  playerId:     number;
  playerName:   string;
  playerPhoto:  string | null;
  parentPhotos: Record<string, string>;
  senders:      SenderConfig[];
  allPlayers:   PlayerResponse[];
}

function Avatar({ photo, name, isMine }: { photo?: string | null; name: string; isMine?: boolean }) {
  if (photo) {
    return <img src={photo} alt={name} className={isMine ? styles.chatAvatarLeft : styles.chatAvatarRight} />;
  }
  return (
    <div className={isMine ? styles.chatAvatarLeft : styles.chatAvatarRight}>
      {name.charAt(0).toUpperCase()}
    </div>
  );
}

export default function FeedbackSection({
  feedbacks, sendFeedback,
  playerId, playerName, playerPhoto, parentPhotos,
  senders, allPlayers,
}: Props) {
  const [msg, setMsg] = useState('');
  const [sending, setSending] = useState(false);

  // recipient tab 목록: 부모(엄마/아빠) + 다른 플레이어
  const otherPlayers = allPlayers.filter(p => p.id !== playerId && p.role === 'player');
  const recipientTabs: string[] = [
    ...senders.map(s => s.label),
    ...otherPlayers.map(p => p.name),
  ];
  const [selectedRecipient, setSelectedRecipient] = useState<string>(recipientTabs[0] ?? '');

  // 선택된 수신자와의 대화 필터링
  const conversationFeedbacks = (() => {
    if (!selectedRecipient) return [];
    const isParent = senders.some(s => s.label === selectedRecipient);

    if (isParent) {
      // 나 → 부모 메세지 (recipient=부모 OR null인 기존 데이터)
      return feedbacks.filter(fb =>
        fb.player_id === playerId &&
        (fb.recipient === selectedRecipient || fb.recipient == null)
      );
    }

    // 아이끼리: 나 → 상대 + 상대 → 나
    const other = allPlayers.find(p => p.name === selectedRecipient);
    if (!other) return [];
    return feedbacks.filter(fb =>
      (fb.player_id === playerId && fb.recipient === selectedRecipient) ||
      (fb.player_id === other.id && fb.recipient === playerName)
    );
  })();

  // 수신자 아바타 사진
  const getRecipientPhoto = (name: string): string | null => {
    const sender = senders.find(s => s.label === name);
    if (sender) return parentPhotos[sender.key] ?? null;
    const p = allPlayers.find(pl => pl.name === name);
    return p?.photo ?? null;
  };

  // 발신자 사진 (replies용)
  const getReplyPhoto = (sender: string): string | null => {
    if (sender === playerName) return playerPhoto;
    return getRecipientPhoto(sender);
  };

  const handleSend = async () => {
    if (!msg.trim() || !selectedRecipient) return;
    setSending(true);
    try {
      await sendFeedback(msg.trim(), selectedRecipient);
      setMsg('');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className={styles.feedbackCard}>
      <div className={styles.feedbackTitle}>💬 가족 채팅</div>

      {/* 수신자 탭 */}
      {recipientTabs.length > 0 && (
        <div className={styles.recipientTabBar}>
          {recipientTabs.map(tab => (
            <button
              key={tab}
              className={`${styles.recipientTab} ${selectedRecipient === tab ? styles.recipientTabActive : ''}`}
              onClick={() => setSelectedRecipient(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
      )}

      {/* 대화 목록 */}
      <div className={styles.chatList}>
        {conversationFeedbacks.length === 0 ? (
          <div className={styles.emptyMsg}>{selectedRecipient}에게 첫 메세지를 보내보세요!</div>
        ) : (
          conversationFeedbacks.map(fb => {
            const isMine = fb.player_id === playerId;
            const senderName = fb.player_name ?? playerName;
            return (
              <div key={fb.id} className={styles.chatThread}>
                {/* 메세지 */}
                <div className={isMine ? styles.chatRowLeft : styles.chatRowRight}>
                  {isMine && <Avatar photo={playerPhoto} name={senderName} isMine />}
                  <div className={isMine ? styles.chatBubbleLeft : styles.chatBubbleRight}>
                    <span className={styles.chatSenderLabel}>{senderName}</span>
                    <p className={styles.chatBubbleText}>{fb.msg}</p>
                  </div>
                  {!isMine && <Avatar photo={getRecipientPhoto(senderName)} name={senderName} />}
                </div>

                {/* 답글 (부모 탭에서 주로 표시) */}
                {fb.replies.map(r => {
                  const replyIsMine = r.sender === playerName;
                  const bubbleClass = replyIsMine
                    ? styles.chatBubbleLeft
                    : r.sender === '아빠' ? `${styles.chatBubbleRight} ${styles.chatBubbleDad}`
                    : r.sender === '엄마' ? `${styles.chatBubbleRight} ${styles.chatBubbleMom}`
                    : styles.chatBubbleRight;
                  return (
                    <div key={r.id} className={replyIsMine ? styles.chatRowLeft : styles.chatRowRight}>
                      {replyIsMine && <Avatar photo={playerPhoto} name={r.sender} isMine />}
                      <div className={bubbleClass}>
                        <span className={styles.chatSenderLabel}>{r.sender}</span>
                        <p className={styles.chatBubbleText}>{r.text}</p>
                      </div>
                      {!replyIsMine && <Avatar photo={getReplyPhoto(r.sender)} name={r.sender} />}
                    </div>
                  );
                })}
              </div>
            );
          })
        )}
      </div>

      {/* 메세지 입력 */}
      <div className={styles.feedbackInputRow}>
        <input
          className={styles.feedbackInput}
          placeholder={`${selectedRecipient || '수신자'}에게 메세지`}
          value={msg}
          onChange={e => setMsg(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          maxLength={500}
        />
        <button
          className={styles.feedbackSend}
          onClick={handleSend}
          disabled={sending || !selectedRecipient}
        >
          전송
        </button>
      </div>
    </div>
  );
}
