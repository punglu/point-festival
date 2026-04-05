import { useState, useEffect, useRef, useCallback } from 'react';
import { httpClient } from '../../api/httpClient';
import styles from './ChatModal.module.css';

interface ChatPartner {
  player_id: number;
  name: string;
  photo: string | null;
  last_message: string | null;
  last_message_at: string | null;
  unread_count: number;
}

interface ChatMessage {
  id: number;
  sender_id: number;
  receiver_id: number;
  message: string;
  is_read: boolean;
  created_at: string;
  sender_name: string | null;
  sender_photo: string | null;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  myId: number;
  myName: string;
  embedded?: boolean;
}

function Avatar({ name, photo, size = 32 }: { name: string; photo?: string | null; size?: number }) {
  if (photo) {
    return (
      <img
        src={photo}
        alt={name}
        className={styles.avatar}
        style={{ width: size, height: size }}
      />
    );
  }
  return (
    <div className={styles.avatarInitial} style={{ width: size, height: size, fontSize: size * 0.4 }}>
      {name.charAt(0)}
    </div>
  );
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  const h = d.getHours();
  const m = String(d.getMinutes()).padStart(2, '0');
  return h < 12 ? `오전 ${h || 12}:${m}` : `오후 ${h - 12 || 12}:${m}`;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export default function ChatModal({ isOpen, onClose, myId, myName: _myName, embedded = false }: Props) {
  const [partners, setPartners]           = useState<ChatPartner[]>([]);
  const [selectedPartner, setSelectedPartner] = useState<ChatPartner | null>(null);
  const [messages, setMessages]           = useState<ChatMessage[]>([]);
  const [inputText, setInputText]         = useState('');
  const [loading, setLoading]             = useState(false);
  const [playerListOpen, setPlayerListOpen] = useState(false);
  const messagesEndRef                    = useRef<HTMLDivElement>(null);
  const pollRef                           = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadPartners = useCallback(async () => {
    try {
      const res = await httpClient.get<ChatPartner[]>('/api/chat/partners');
      setPartners(res.data);
    } catch { /* silent */ }
  }, []);

  const loadHistory = useCallback(async (partnerId: number) => {
    setLoading(true);
    try {
      const res = await httpClient.get<ChatMessage[]>(`/api/chat/history/${partnerId}`);
      setMessages(res.data.slice().reverse());
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, []);

  // 파트너 목록 초기 로드
  useEffect(() => {
    if (!isOpen) return;
    loadPartners();
  }, [isOpen, loadPartners]);

  // 대화 선택 시 히스토리 로드 + 파트너 언리드 초기화
  useEffect(() => {
    if (!selectedPartner) return;
    loadHistory(selectedPartner.player_id);
    setPartners(prev =>
      prev.map(p => p.player_id === selectedPartner.player_id ? { ...p, unread_count: 0 } : p)
    );
  }, [selectedPartner, loadHistory]);

  // 15초 폴링
  useEffect(() => {
    if (!isOpen) return;
    pollRef.current = setInterval(() => {
      loadPartners();
      if (selectedPartner) loadHistory(selectedPartner.player_id);
    }, 15000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [isOpen, selectedPartner, loadPartners, loadHistory]);

  // 메시지 추가 시 스크롤 맨 아래
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const text = inputText.trim();
    if (!text || !selectedPartner) return;
    setInputText('');
    try {
      const res = await httpClient.post<ChatMessage>('/api/chat/send', {
        receiver_id: selectedPartner.player_id,
        message: text,
      });
      setMessages(prev => [...prev, res.data]);
      loadPartners();
    } catch { /* silent */ }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  if (!isOpen && !embedded) return null;

  const content = (
    <div className={`${styles.modal} ${embedded ? styles.embedded : ''}`}>
      {/* 모바일 아코디언 토글 — 데스크탑 숨김, embedded 전용 */}
      {embedded && (
        <button
          className={styles.accordionToggle}
          onClick={() => setPlayerListOpen(prev => !prev)}
        >
          <span className={styles.toggleIcon}>{playerListOpen ? '▲' : '▼'}</span>
          <span>{selectedPartner ? selectedPartner.name : '사용자 선택'}</span>
          <span className={styles.toggleHint}>{playerListOpen ? '접기' : '목록 보기'}</span>
        </button>
      )}

      {/* 좌측: 대화 상대 사이드바 */}
      <div className={[
        styles.sidebar,
        embedded ? styles.sidebarWide : '',
        embedded ? styles.playerListWrapper : '',
        embedded && playerListOpen ? styles.playerListOpen : '',
      ].filter(Boolean).join(' ')}>
        <div className={styles.sidebarHeader}>
          {embedded ? '대화 목록' : '💬'}
        </div>
        <div className={styles.partnerList}>
          {partners.map(p => (
            <button
              key={p.player_id}
              className={`${styles.partnerItem} ${selectedPartner?.player_id === p.player_id ? styles.partnerActive : ''}`}
              onClick={() => { setSelectedPartner(p); if (embedded) setPlayerListOpen(false); }}
            >
              <div className={styles.partnerAvatarWrap}>
                <Avatar name={p.name} photo={p.photo} size={36} />
                {p.unread_count > 0 && (
                  <span className={styles.unreadDot}>{p.unread_count}</span>
                )}
              </div>
              <div className={styles.partnerInfo}>
                <div className={styles.partnerName}>{p.name}</div>
                {p.last_message && (
                  <div className={styles.partnerPreview}>{p.last_message}</div>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 우측: 대화 창 */}
      <div className={styles.chatArea}>
        {!selectedPartner ? (
          <div className={styles.noPartner}>대화 상대를 선택하세요</div>
        ) : (
          <>
            {/* 헤더 */}
            <div className={styles.chatHeader}>
              <Avatar name={selectedPartner.name} photo={selectedPartner.photo} size={28} />
              <span className={styles.chatPartnerName}>{selectedPartner.name}</span>
              {!embedded && (
                <button className={styles.closeBtn} onClick={onClose}>✕</button>
              )}
            </div>

            {/* 메시지 목록 */}
            <div className={styles.messageList}>
              {loading && <div className={styles.loadingMsg}>로딩 중...</div>}
              {messages.map(msg => {
                const isMine = msg.sender_id === myId;
                return (
                  <div key={msg.id} className={`${styles.msgRow} ${isMine ? styles.mine : styles.theirs}`}>
                    {!isMine && (
                      <Avatar name={msg.sender_name ?? ''} photo={msg.sender_photo} size={26} />
                    )}
                    <div className={styles.msgContent}>
                      {!isMine && <div className={styles.senderName}>{msg.sender_name}</div>}
                      <div className={styles.msgBubble}>
                        <span className={styles.msgText}>{msg.message}</span>
                        <span className={styles.msgTime}>{formatTime(msg.created_at)}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* 입력창 */}
            <div className={styles.inputArea}>
              <input
                className={styles.inputBox}
                placeholder="메시지를 입력하세요..."
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                maxLength={500}
              />
              <button className={styles.sendBtn} onClick={handleSend} disabled={!inputText.trim()}>
                전송
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );

  if (embedded) return content;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.overlayInner} onClick={e => e.stopPropagation()}>
        {content}
      </div>
    </div>
  );
}
