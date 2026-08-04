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
 *
 * MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001: the room pane
 * (header/thread/composer) now renders the canonical `FamilyChatScreen` (1d)
 * instead of ad hoc JSX — this file is now the Product Container/adapter, the
 * Screen is the single presentational source shared with `FamilyChatPreview`.
 * The room-list sidebar and every overlay stay exactly as they were: they are
 * real Product Container concerns (navigation, real API/hooks), not part of
 * the 1d canonical contract.
 */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import {
  listMessages,
  listParticipants,
  listRoomSummaries,
  sendMessage,
  type WagleMessage,
  type WagleParticipant,
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
import { FamilyChatScreen } from '../../screens/wagle/FamilyChat';
import type { FamilyChatMessage, FamilyChatModel } from '../../screens/wagle/FamilyChat';
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

// W7.5: member list now calls the real GET .../participants (required an
// additive `account_display_name` field on `ParticipantResponse`, same gap
// shape as `1q`'s `MembershipSummary` fix). No file-listing API exists yet
// (TRUE_FUNCTIONAL_GAP) — file list still uses the canonical fixture as an
// explicit pending adapter. Per-room mute/notification toggles remain
// unwired: D6-P2, a registered PM policy decision, not missing engineering.
function buildChatSettingsModel(roomTitle: string, members: WagleParticipant[] | null): ChatSettingsModel {
  return {
    ...chatSettingsFixture,
    roomName: roomTitle,
    memberSummary: members ? `${members.length}명` : chatSettingsFixture.memberSummary,
    members: members ? members.map((m) => ({ name: m.account_display_name })) : chatSettingsFixture.members,
  };
}

function buildFileViewerModel(roomTitle: string): FileViewerModel {
  return { ...fileViewerFixture, subtitle: roomTitle };
}

// Real-data adapter for the 1d canonical Screen (product integration,
// W7.4-WAGLE-SINGLE-SOURCE-001). `ownParticipantId` is resolved from the
// signed-in account's own `family_membership_id` against this room's real
// participants (see `ownParticipantId` below) — previously this was a
// disclosed `null` gap ("no participant lookup wired yet") on the 2g
// adapter; participants are now loaded whenever a room is selected (not only
// when the settings overlay opens), so both the header avatar stack and this
// own/other split use the same real fetch.
function toFamilyChatMessages(
  messages: WagleMessage[],
  ownParticipantId: string | null,
  participantNameById: Map<string, string>,
): FamilyChatMessage[] {
  const messageBodyById = new Map<string, string>();
  for (const m of messages) if (!m.deleted && m.body) messageBodyById.set(String(m.id), m.body);

  return messages.map((message) => {
    const time = new Date(message.created_at).toLocaleTimeString('ko-KR', {
      hour: 'numeric',
      minute: '2-digit',
    });

    if (message.message_type === 'SERVICE_ACTION') {
      return {
        id: String(message.id),
        kind: 'service',
        body: message.body,
        deleted: message.deleted,
        tombstone: message.tombstone,
        time,
        serviceBadge: message.service_code ?? '서비스',
      };
    }

    const isOwn = message.sender_participant_id !== null && message.sender_participant_id === ownParticipantId;
    return {
      id: String(message.id),
      kind: isOwn ? 'own' : 'other',
      authorName: isOwn
        ? undefined
        : (message.sender_participant_id && participantNameById.get(message.sender_participant_id)) || '가족',
      body: message.body,
      deleted: message.deleted,
      tombstone: message.tombstone,
      time,
      replyPreview: message.reply_to_message_id
        ? messageBodyById.get(String(message.reply_to_message_id))
        : undefined,
    };
  });
}

export function WagleRoomView() {
  const context = useFamilyContextStore((s) => s.context);
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const [state, setState] = useState<ScreenState>('loading');
  const [rooms, setRooms] = useState<WagleRoomSummary[]>([]);
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
  const [messages, setMessages] = useState<WagleMessage[]>([]);
  const [draft, setDraft] = useState('');
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [replyTarget, setReplyTarget] = useState<WagleMessage | null>(null);
  const [showReplyOverlay, setShowReplyOverlay] = useState(false);
  const [activeOverlay, setActiveOverlay] = useState<'none' | 'settings' | 'files'>('none');
  const [roomParticipants, setRoomParticipants] = useState<WagleParticipant[] | null>(null);
  const [, setSearchParams] = useSearchParams();

  // MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001: participants now
  // load whenever a room is selected, not only when the settings overlay
  // opens — the canonical 1d header's avatar stack and own/other bubble split
  // need this same real list. `MongleAppShell`'s `isWagleConversationMobile`
  // mobile-header-hiding switch (Wave 6.0B §6.1) reads this room id back out
  // of the URL, which is why `selectedRoomId` is mirrored into `?room=` below.
  useEffect(() => {
    if (activeFamilyId === null || !selectedRoomId) {
      setRoomParticipants(null);
      return undefined;
    }
    const controller = new AbortController();
    listParticipants(activeFamilyId, selectedRoomId, controller.signal)
      .then(setRoomParticipants)
      .catch(() => setRoomParticipants([]));
    return () => controller.abort();
  }, [activeFamilyId, selectedRoomId]);

  useEffect(() => {
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        if (selectedRoomId) next.set('room', selectedRoomId);
        else next.delete('room');
        return next;
      },
      { replace: true },
    );
  }, [selectedRoomId, setSearchParams]);

  const selectedRoom = useMemo(
    () => rooms.find((r) => String(r.id) === selectedRoomId) ?? null,
    [rooms, selectedRoomId],
  );

  const participantNameById = useMemo(() => {
    const map = new Map<string, string>();
    for (const p of roomParticipants ?? []) map.set(p.id, p.account_display_name);
    return map;
  }, [roomParticipants]);

  const myMembershipId = useMemo(
    () => context?.families.find((f) => f.id === activeFamilyId)?.membership.id ?? null,
    [context, activeFamilyId],
  );

  const ownParticipantId = useMemo(
    () => roomParticipants?.find((p) => p.family_membership_id === myMembershipId)?.id ?? null,
    [roomParticipants, myMembershipId],
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
        // canonical 2g (채팅 답장, W7.5 Phase C): the backend's
        // `reply_to_message_id` column already existed and was simply never
        // exposed. The frozen 2g overlay itself has no editable text input
        // (its `.inputText` renders a static fixture string, not a real
        // `<input>`) -- so the quote-and-reply gesture is real (tap ↩ on a
        // message, see it quoted, confirm), but the actual typing happens in
        // this always-real composer, which now carries the pending reply
        // target through to the request.
        reply_to_message_id: replyTarget ? String(replyTarget.id) : undefined,
      });
      setDraft('');
      setReplyTarget(null);
      await loadMessages(activeFamilyId, selectedRoomId);
    } catch (error: unknown) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setSendError(detail ?? '메시지를 보내지 못했어요.');
    } finally {
      setSending(false);
    }
  };

  const familyChatModel: FamilyChatModel | null = useMemo(() => {
    if (!selectedRoom) return null;
    return {
      roomTitle: selectedRoom.title ?? '가족 대화',
      participants: (roomParticipants ?? []).map((p) => ({ id: p.id, name: p.account_display_name })),
      connectionState,
      connectionLabel: CONNECTION_LABEL[connectionState],
      messages: toFamilyChatMessages(messages, ownParticipantId, participantNameById),
      draft,
      sending,
      sendError,
      replyBannerText: replyTarget && !showReplyOverlay ? (replyTarget.body ?? '') : null,
    };
  }, [
    selectedRoom,
    roomParticipants,
    connectionState,
    messages,
    ownParticipantId,
    participantNameById,
    draft,
    sending,
    sendError,
    replyTarget,
    showReplyOverlay,
  ]);

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
        {selectedRoom && familyChatModel ? (
          <FamilyChatScreen
            model={familyChatModel}
            onBack={() => setSelectedRoomId(null)}
            onDraftChange={setDraft}
            onSend={() => void handleSend()}
            onReplyMessage={(messageId) => {
              const target = messages.find((m) => String(m.id) === messageId);
              if (target) {
                setReplyTarget(target);
                setShowReplyOverlay(true);
              }
            }}
            onCancelReply={() => setReplyTarget(null)}
            onOpenSettings={() => setActiveOverlay('settings')}
            onOpenFiles={() => setActiveOverlay('files')}
          />
        ) : (
          <p className={styles.empty}>대화방을 선택해주세요.</p>
        )}
      </div>

      {replyTarget && showReplyOverlay && (
        <div className={styles.replyOverlay} data-testid="wagle-reply-overlay">
          {/* canonical 2g (채팅 답장) -- quote is real (`replyTarget.body`).
              `onSend` closes this overlay back to the room, keeping
              `replyTarget` so the always-real composer below carries the
              reply through; `onCancelQuote` is the only path that actually
              drops the pending reply. See `handleSend`'s own comment for why
              typing happens there and not in this overlay. */}
          <ChatReplyScreen
            model={buildChatReplyModel(replyTarget, selectedRoom?.title ?? '가족 대화')}
            onCancelQuote={() => { setReplyTarget(null); setShowReplyOverlay(false); }}
            onSend={() => setShowReplyOverlay(false)}
          />
        </div>
      )}
      {activeOverlay === 'settings' && (
        <div className={styles.replyOverlay} data-testid="wagle-settings-overlay">
          <ChatSettingsScreen
            model={buildChatSettingsModel(selectedRoom?.title ?? '가족 대화', roomParticipants)}
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
