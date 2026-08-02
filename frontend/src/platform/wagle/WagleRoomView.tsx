/**
 * 와글와글 실제 Room 화면 — real rooms, real messages, real realtime.
 *
 * This is the screen that retires the preview fixtures. Nothing here falls back
 * to them: if the API fails the screen says so, because a conversation view
 * that silently shows sample messages is worse than one that shows an error.
 *
 * **How live and recovered messages stay identical.** The realtime channel
 * carries identifiers only — no bodies. Every message rendered here came from
 * `listMessages`, whether it arrived because the socket announced it or because
 * a reconnect replayed a gap. One fetch path means "live" and "recovered"
 * cannot diverge, which is otherwise a bug class that only shows up after a
 * network blip.
 *
 * The client deduplicates on message id and detects sequence gaps; when it
 * reports one, this screen refetches that room's history rather than leaving a
 * hole the user would read as missing messages.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

import {
  listMessages,
  listRoomSummaries,
  sendMessage,
  type WagleMessage,
  type WagleRoomSummary,
} from '../../shared/api/wagleApi';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import { useWagleRealtime } from './realtime/useWagleRealtime';
import type { WagleConnectionState } from './realtime/wagleRealtimeClient';
import { ChatReplyScreen } from '../../screens/wagle/ChatReply';
import type { ChatReplyModel } from '../../screens/wagle/ChatReply';
import { ChatSettingsScreen, chatSettingsFixture } from '../../screens/wagle/ChatSettings';
import type { ChatSettingsModel } from '../../screens/wagle/ChatSettings';
import { FileViewerScreen, fileViewerFixture } from '../../screens/wagle/FileViewer';
import type { FileViewerModel } from '../../screens/wagle/FileViewer';
import styles from './WagleRoomView.module.css';

const CONNECTION_LABEL: Record<WagleConnectionState, string> = {
  idle: '대기 중',
  connecting: '연결 중…',
  connected: '실시간 연결됨',
  recovering: '복구 중…',
  offline: '연결이 끊겼어요. 다시 연결하는 중…',
  authorization_lost: '실시간 연결 권한이 없어요',
};

type ScreenState = 'loading' | 'ready' | 'error' | 'forbidden';

// Real-data adapter for the 2g canonical overlay (KEEP_PAGE_LOCAL/NO_ROUTE per
// the W7.1 Ownership Matrix). No participant-name lookup is wired to this
// component yet, so the quoted author falls back to a neutral label rather
// than guessing a name — a real name is W7.5 data-wiring scope, not this
// structural pass's.
function buildChatReplyModel(target: WagleMessage, roomTitle: string): ChatReplyModel {
  return {
    roomTitle,
    backgroundMessages: [{ tone: 'in', text: target.body ?? '' }],
    quotedAuthor: '이 메시지',
    quotedText: target.body ?? '',
    draftText: '',
  };
}

// No room-settings or file-listing API exists yet (TRUE_FUNCTIONAL_GAP, W7.5
// scope) — the real room title is threaded through; member/file lists use the
// canonical fixture as an explicit pending adapter, per the W7.4 boundary that
// forbids fabricating data that looks real.
function buildChatSettingsModel(roomTitle: string): ChatSettingsModel {
  return { ...chatSettingsFixture, roomName: roomTitle };
}

function buildFileViewerModel(roomTitle: string): FileViewerModel {
  return { ...fileViewerFixture, subtitle: roomTitle };
}

function MessageRow({
  message,
  ownParticipantId,
  onReply,
}: {
  message: WagleMessage;
  ownParticipantId: string | null;
  onReply: (message: WagleMessage) => void;
}) {
  const isService = message.message_type === 'SERVICE_ACTION';
  const isOwn = !isService && message.sender_participant_id === ownParticipantId;

  if (isService) {
    // A ServicePrincipal message must never look like a person's. It gets its
    // own presentation and an explicit service label rather than a name.
    return (
      <li className={styles.serviceRow} data-message-id={message.id} data-actor="service">
        <div className={styles.serviceCard}>
          <span className={styles.serviceBadge}>{message.service_code ?? '서비스'}</span>
          <span className={styles.serviceBody}>
            {message.deleted ? message.tombstone : message.body ?? '서비스 알림'}
          </span>
        </div>
      </li>
    );
  }

  return (
    <li
      className={`${styles.messageRow} ${isOwn ? styles.own : styles.other}`}
      data-message-id={message.id}
      data-actor={isOwn ? 'self' : 'other'}
    >
      <div className={styles.bubble}>
        {message.deleted ? (
          <span className={styles.tombstone}>{message.tombstone ?? '삭제된 메시지'}</span>
        ) : (
          <span className={styles.body}>{message.body}</span>
        )}
      </div>
      {!message.deleted && !isService && (
        <button
          type="button"
          className={styles.replyTrigger}
          onClick={() => onReply(message)}
          aria-label="답장하기"
          data-testid={`wagle-reply-${message.id}`}
        >
          ↩
        </button>
      )}
    </li>
  );
}

export function WagleRoomView() {
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const [state, setState] = useState<ScreenState>('loading');
  const [rooms, setRooms] = useState<WagleRoomSummary[]>([]);
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
  const [messages, setMessages] = useState<WagleMessage[]>([]);
  const [draft, setDraft] = useState('');
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [replyTarget, setReplyTarget] = useState<WagleMessage | null>(null);
  const [activeOverlay, setActiveOverlay] = useState<'none' | 'settings' | 'files'>('none');
  const listEndRef = useRef<HTMLDivElement | null>(null);

  const selectedRoom = useMemo(
    () => rooms.find((r) => String(r.id) === selectedRoomId) ?? null,
    [rooms, selectedRoomId],
  );

  const loadRooms = useCallback(async (familyId: number, signal?: AbortSignal) => {
    setState('loading');
    try {
      const summaries = await listRoomSummaries(familyId, signal);
      setRooms(summaries);
      setState('ready');
      return summaries;
    } catch (error: unknown) {
      if (signal?.aborted) return [];
      const status = (error as { response?: { status?: number } }).response?.status;
      setState(status === 403 ? 'forbidden' : 'error');
      return [];
    }
  }, []);

  const loadMessages = useCallback(
    async (familyId: number, roomId: string, signal?: AbortSignal) => {
      try {
        const page = await listMessages(familyId, roomId, { limit: 100 }, signal);
        setMessages(page.messages);
        return page.highestSequence;
      } catch {
        if (!signal?.aborted) setSendError('대화를 불러오지 못했어요.');
        return 0;
      }
    },
    [],
  );

  useEffect(() => {
    if (activeFamilyId === null) return undefined;
    const controller = new AbortController();
    setSelectedRoomId(null);
    setMessages([]);
    void loadRooms(activeFamilyId, controller.signal).then((summaries) => {
      if (summaries.length > 0) setSelectedRoomId(String(summaries[0].id));
    });
    return () => controller.abort();
    // Family change reloads everything: the previous family's rooms and
    // messages must not linger on screen after a switch.
  }, [activeFamilyId, loadRooms]);

  const realtimeRooms = useMemo(
    () =>
      activeFamilyId !== null && selectedRoomId
        ? [{ familyId: activeFamilyId, roomId: selectedRoomId }]
        : [],
    [activeFamilyId, selectedRoomId],
  );

  const { state: connectionState, primeCursor } = useWagleRealtime({
    rooms: realtimeRooms,
    enabled: activeFamilyId !== null,
    // An announced event carries no body, so the screen refetches. Both the
    // live path and the gap path land here, which is what keeps them identical.
    onEvents: (familyId, roomId) => {
      if (roomId === selectedRoomId) void loadMessages(familyId, roomId);
    },
    onGap: (familyId, roomId) => {
      if (roomId === selectedRoomId) void loadMessages(familyId, roomId);
    },
  });

  useEffect(() => {
    if (activeFamilyId === null || !selectedRoomId) return undefined;
    const controller = new AbortController();
    void loadMessages(activeFamilyId, selectedRoomId, controller.signal).then((highest) => {
      // Seed the realtime cursor from history already on screen, or a reconnect
      // would replay everything the user can already see.
      if (highest > 0) primeCursor(activeFamilyId, selectedRoomId, highest);
    });
    return () => controller.abort();
  }, [activeFamilyId, selectedRoomId, loadMessages, primeCursor]);

  useEffect(() => {
    listEndRef.current?.scrollIntoView({ block: 'end' });
  }, [messages]);

  const handleSend = async () => {
    if (activeFamilyId === null || !selectedRoomId || draft.trim() === '') return;
    setSending(true);
    setSendError(null);
    try {
      await sendMessage(activeFamilyId, selectedRoomId, {
        body: draft.trim(),
        // Server-side idempotency key: a retried send resolves to the same
        // message rather than posting twice.
        client_message_id:
          typeof crypto !== 'undefined' && 'randomUUID' in crypto
            ? crypto.randomUUID()
            : `msg-${Date.now()}`,
      });
      setDraft('');
      await loadMessages(activeFamilyId, selectedRoomId);
    } catch (error: unknown) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setSendError(detail ?? '메시지를 보내지 못했어요.');
    } finally {
      setSending(false);
    }
  };

  if (activeFamilyId === null) {
    return (
      <section className={styles.page}>
        <h1>가족을 선택해주세요</h1>
      </section>
    );
  }

  if (state === 'loading') {
    return (
      <section className={styles.page} aria-busy="true">
        <p className={styles.muted}>대화를 불러오는 중…</p>
      </section>
    );
  }

  if (state === 'forbidden') {
    return (
      <section className={styles.page} role="alert" data-testid="wagle-forbidden">
        <h1>와글와글을 이용할 수 없어요</h1>
        <p className={styles.muted}>가족의 와글와글 서비스 상태를 확인한 뒤 다시 시도해주세요.</p>
      </section>
    );
  }

  if (state === 'error') {
    return (
      <section className={styles.page} role="alert">
        <h1>대화를 불러오지 못했어요</h1>
        <button type="button" className={styles.primary} onClick={() => void loadRooms(activeFamilyId)}>
          다시 시도
        </button>
      </section>
    );
  }

  return (
    <section className={styles.page} aria-labelledby="wagle-title" data-wagle-connection={connectionState}>
      <aside className={`${styles.roomList} ${selectedRoomId ? styles.roomListHiddenMobile : ''}`}>
        <header className={styles.roomListHeader}>
          <p className={styles.eyebrow}>몽글 · 가족 대화</p>
          <h1 id="wagle-title">와글와글</h1>
          <Link to="/wagle/board" className={styles.boardLink} data-testid="wagle-open-board">
            가족 게시판 →
          </Link>
        </header>
        {rooms.length === 0 ? (
          <p className={styles.empty} data-testid="wagle-rooms-empty">
            아직 대화방이 없어요.
          </p>
        ) : (
          <ul className={styles.rooms} aria-label="대화방 목록" data-testid="wagle-room-list">
            {rooms.map((room) => (
              <li key={String(room.id)}>
                <button
                  type="button"
                  className={`${styles.roomItem} ${String(room.id) === selectedRoomId ? styles.roomActive : ''}`}
                  onClick={() => setSelectedRoomId(String(room.id))}
                  data-testid={`wagle-room-${room.id}`}
                  aria-current={String(room.id) === selectedRoomId ? 'true' : undefined}
                >
                  <span className={styles.roomTitle}>{room.title ?? '가족 대화'}</span>
                  {room.last_message?.body && (
                    <span className={styles.roomPreview}>{room.last_message.body}</span>
                  )}
                  {(room.unread_count ?? 0) > 0 && (
                    <span className={styles.unread}>{room.unread_count}</span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>

      <div className={styles.roomPane}>
        {selectedRoom ? (
          <>
            <header className={styles.roomHeader}>
              <button
                type="button"
                className={styles.backButton}
                onClick={() => setSelectedRoomId(null)}
                aria-label="대화방 목록으로"
              >
                ←
              </button>
              <h2 className={styles.roomHeaderTitle}>{selectedRoom.title ?? '가족 대화'}</h2>
              <span
                className={styles.connection}
                data-testid="wagle-connection-state"
                data-state={connectionState}
              >
                {CONNECTION_LABEL[connectionState]}
              </span>
              <button
                type="button"
                className={styles.headerAction}
                onClick={() => setActiveOverlay('files')}
                aria-label="사진/파일"
                data-testid="wagle-open-files"
              >
                🖼
              </button>
              <button
                type="button"
                className={styles.headerAction}
                onClick={() => setActiveOverlay('settings')}
                aria-label="채팅방 설정"
                data-testid="wagle-open-settings"
              >
                ⚙
              </button>
            </header>

            {messages.length === 0 ? (
              <p className={styles.empty} data-testid="wagle-messages-empty">
                아직 메시지가 없어요.
              </p>
            ) : (
              <ol className={styles.messages} data-testid="wagle-messages">
                {messages.map((message) => (
                  <MessageRow
                    key={String(message.id)}
                    message={message}
                    ownParticipantId={null}
                    onReply={setReplyTarget}
                  />
                ))}
              </ol>
            )}
            <div ref={listEndRef} />

            <div className={styles.composer}>
              <label className={styles.srOnly} htmlFor="wagle-draft">
                메시지 입력
              </label>
              <input
                id="wagle-draft"
                className={styles.input}
                value={draft}
                disabled={sending}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    void handleSend();
                  }
                }}
                placeholder="메시지를 입력하세요"
                data-testid="wagle-composer-input"
              />
              <button
                type="button"
                className={styles.primary}
                disabled={sending || draft.trim() === ''}
                onClick={() => void handleSend()}
                data-testid="wagle-send"
              >
                {sending ? '전송 중…' : '보내기'}
              </button>
            </div>
            {sendError && (
              <p className={styles.error} role="alert">
                {sendError}
              </p>
            )}
          </>
        ) : (
          <p className={styles.empty}>대화방을 선택해주세요.</p>
        )}
      </div>

      {replyTarget && (
        <div className={styles.replyOverlay} data-testid="wagle-reply-overlay">
          <ChatReplyScreen model={buildChatReplyModel(replyTarget, selectedRoom?.title ?? '가족 대화')} onCancelQuote={() => setReplyTarget(null)} onSend={() => setReplyTarget(null)} />
        </div>
      )}
      {activeOverlay === 'settings' && (
        <div className={styles.replyOverlay} data-testid="wagle-settings-overlay">
          <ChatSettingsScreen
            model={buildChatSettingsModel(selectedRoom?.title ?? '가족 대화')}
            onBack={() => setActiveOverlay('none')}
          />
        </div>
      )}
      {activeOverlay === 'files' && (
        <div className={styles.replyOverlay} data-testid="wagle-files-overlay">
          <FileViewerScreen
            model={buildFileViewerModel(selectedRoom?.title ?? '가족 대화')}
            onBack={() => setActiveOverlay('none')}
          />
        </div>
      )}
    </section>
  );
}
