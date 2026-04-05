import { useState, useEffect, useCallback } from 'react';
import styles from './FeedbackView.module.css';
import { getMonday, getWeekDates } from '../../../../shared/utils/dateUtils';
import { adminApi } from '../../api/adminApi';
import { useAdminAuth } from '../../hooks/useAdminAuth';
import PlayerTab from '../../components/PlayerTab/PlayerTab';
import type { Player, FeedbackItem } from '../../types/admin.types';

function getWeekDays(weekStart: string): string[] {
  return getWeekDates(weekStart);
}

function dayLabel(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00');
  const days = ['일', '월', '화', '수', '목', '금', '토'];
  return `${dateStr.slice(5)} (${days[d.getDay()]})`;
}

/* ── 아바타 ── */
function Avatar({ name, photo, isMe }: { name: string; photo?: string | null; isMe: boolean }) {
  if (photo) {
    return <img src={photo} alt={name} className={isMe ? styles.avatarMe : styles.avatarOther} style={{ objectFit: 'cover' }} />;
  }
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

  const [players,      setPlayers]      = useState<Player[]>([]);
  const [parentPhotos, setParentPhotos] = useState<Record<string, string>>({});
  const [selected,     setSelected]     = useState<number | null>(null);
  const [weekStart,    setWeekStart]    = useState(() => getMonday());
  const [feedbacks,    setFeedbacks]    = useState<FeedbackItem[]>([]);
  const [loading,      setLoading]      = useState(false);

  /* 플레이어 목록 */
  useEffect(() => {
    const ctrl = new AbortController();
    adminApi.getPlayers(ctrl.signal)
      .then(r => setPlayers(r.data.filter(p => p.role === 'player')))
      .catch(() => {});
    return () => ctrl.abort();
  }, []);

  /* 부모(관리자) 사진 로드 */
  useEffect(() => {
    Promise.all([
      adminApi.getConfig('photos.dad').catch(() => null),
      adminApi.getConfig('photos.mom').catch(() => null),
    ]).then(([dad, mom]) => {
      const photos: Record<string, string> = {};
      if (dad?.data?.value) photos['아빠'] = dad.data.value;
      if (mom?.data?.value) photos['엄마'] = mom.data.value;
      setParentPhotos(photos);
    });
  }, []);

  /* 주간 전체 피드백 로드 — 7일 병렬 fetch, 결과 병합 */
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const days = getWeekDays(weekStart);
      const results = await Promise.all(
        days.map(day => adminApi.getFeedbacks(day, selected ?? undefined).catch(() => ({ data: [] as FeedbackItem[] })))
      );
      const merged = results
        .flatMap(r => r.data)
        .sort((a, b) => a.id - b.id);
      setFeedbacks(merged);
    } catch { /* silent */ } finally {
      setLoading(false);
    }
  }, [weekStart, selected]);

  useEffect(() => { load(); }, [load]);

  /* 답장 전송 */
  const handleReply = async (feedbackId: number, text: string) => {
    await adminApi.sendAdminReply({ feedback_id: feedbackId, sender: senderName, text });
    await load();
  };

  /* 주간 이동 */
  const movePrevWeek = () => setWeekStart(prev => { const d = new Date(prev + 'T00:00:00'); d.setDate(d.getDate() - 7); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; });
  const moveNextWeek = () => setWeekStart(prev => { const d = new Date(prev + 'T00:00:00'); d.setDate(d.getDate() + 7); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; });
  const moveThisWeek = () => setWeekStart(getMonday());

  /* 날짜별 그룹 */
  const grouped = new Map<string, FeedbackItem[]>();
  for (const fb of feedbacks) {
    const arr = grouped.get(fb.date) || [];
    arr.push(fb);
    grouped.set(fb.date, arr);
  }

  /* 주 레이블 */
  const weekLabel = (() => { const s = weekStart.replace(/-/g,'.'); const e = getWeekDates(weekStart)[6].replace(/-/g,'.'); return `${s} ~ ${e}`; })();

  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <h1 className={styles.title}>💬 가족 채팅</h1>
        <span className={styles.senderBadge}>{senderName} 으로 답장</span>
      </div>

      {/* 주간 네비게이션 */}
      <div className={styles.dateRow}>
        <button className={styles.dateBtn} onClick={movePrevWeek}>◀</button>
        <span className={styles.weekLabel}>{weekLabel}</span>
        <button className={styles.dateBtn} onClick={moveNextWeek}>▶</button>
        <button className={styles.todayBtn} onClick={moveThisWeek}>이번 주</button>
      </div>

      {/* 플레이어 탭 */}
      <PlayerTab players={players} selected={selected} onSelect={setSelected} />

      {/* 채팅 목록 */}
      <div className={styles.chatArea}>
        {loading ? (
          <div className={styles.empty}>로딩 중...</div>
        ) : feedbacks.length === 0 ? (
          <div className={styles.empty}>이번 주 메세지가 없습니다.</div>
        ) : (
          [...grouped.entries()].map(([dateStr, dayFeedbacks]) => (
            <div key={dateStr}>
              <div className={styles.dateDivider}>{dayLabel(dateStr)}</div>
              {dayFeedbacks.map(fb => {
                // players 배열에서 이름 확정 (fb.player_name 폴백)
                const playerName = players.find(p => p.id === fb.player_id)?.name
                  ?? fb.player_name
                  ?? `플레이어 ${fb.player_id}`;
                const playerPhoto = players.find(p => p.id === fb.player_id)?.photo ?? null;

                return (
                  <div key={fb.id} className={styles.thread}>
                    {/* 플레이어 메세지 — 좌측 */}
                    <div className={styles.rowLeft}>
                      <Avatar name={playerName} photo={playerPhoto} isMe={false} />
                      <div className={styles.bubblePlayer}>
                        <span className={styles.bubbleSender}>{playerName}</span>
                        <p className={styles.bubbleText}>{fb.msg}</p>
                      </div>
                    </div>

                    {/* 답글 */}
                    {fb.replies.map(r => {
                      const isMe = r.sender === senderName;
                      // 답글 발신자 사진: 관리자면 parentPhotos, 플레이어면 players
                      const replyPhoto = parentPhotos[r.sender]
                        ?? players.find(p => p.name === r.sender)?.photo
                        ?? null;
                      return (
                        <div key={r.id} className={isMe ? styles.rowRight : styles.rowLeft}>
                          {!isMe && <Avatar name={r.sender} photo={replyPhoto} isMe={false} />}
                          <div className={isMe ? styles.bubbleMe : styles.bubbleOther}>
                            <span className={styles.bubbleSender}>{r.sender}</span>
                            <p className={styles.bubbleText}>{r.text}</p>
                          </div>
                          {isMe && <Avatar name={r.sender} photo={parentPhotos[r.sender] ?? null} isMe />}
                        </div>
                      );
                    })}

                    {/* 관리자 답장 입력 */}
                    <ReplyBox feedbackId={fb.id} senderName={senderName} onSend={handleReply} />
                  </div>
                );
              })}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
