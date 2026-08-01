import { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import { Avatar } from '../../shared/components/Avatar';
import {
  ChatHeader,
  RoomItem,
  MessageBubble,
  DateDivider,
  UnreadDivider,
  ChatComposer,
  ServiceActionCard,
  LoadingState,
  EmptyState,
  ErrorState,
  WaglePinLock,
} from '../wagle/components';
import { useWagleRealtime } from '../wagle/realtime/useWagleRealtime';
import {
  waglePreviewRooms,
  waglePreviewRoomLabels,
  waglePreviewMessagesByRoom,
  waglePreviewDefaultConversation,
  waglePreviewServiceEventsByRoom,
  resolvePreviewPageState,
  type WaglePreviewRoom,
  type WaglePreviewPageState,
} from '../wagle/preview';
import styles from './WagleLanding.module.css';

type ComposeStatus = 'idle' | 'pending' | 'failed';

interface ConversationProps {
  room: WaglePreviewRoom;
  onBack: () => void;
}

function Conversation({ room, onBack }: ConversationProps) {
  const [draft, setDraft] = useState('');
  const [composeStatus, setComposeStatus] = useState<ComposeStatus>('idle');
  // SERVICE room만 read-only다 — page-level 강제 read-only는 미승인 정책이라 두지 않는다(Wave 3.1 M4).
  const isReadOnly = room.kind === 'SERVICE';
  const messages = waglePreviewMessagesByRoom[room.id] ?? waglePreviewDefaultConversation;
  const serviceEvent = waglePreviewServiceEventsByRoom[room.id];

  // fixture에 별도 unread marker 필드가 없으므로, room.unread 개수만큼 마지막
  // incoming 메시지 앞에 UnreadDivider를 계산해 배치한다(§9.2 unread/read 표현).
  const unreadDividerIndex = room.unread && room.unread > 0 ? Math.max(0, messages.length - room.unread) : -1;

  const handleSend = () => {
    if (!draft.trim() || isReadOnly) return;
    setComposeStatus('pending');
    window.setTimeout(() => setComposeStatus('failed'), 500);
  };

  const handleRetry = () => setComposeStatus('pending');

  // SERVICE는 사람이 아니므로 참여자 Avatar를 표시하지 않는다 — DIRECT/GROUP만 관계 식별용
  // Avatar를 보여준다(§8.16 avatar stack ≤4). 이름 첫 글자를 fallback으로 쓸 뿐 새 필드는 없다.
  const participants =
    room.kind !== 'SERVICE'
      ? [{ id: room.id, name: room.name, avatarFallback: room.name.trim().charAt(0) || '와' }]
      : undefined;

  return (
    <section className={styles.conversation} aria-label={`${room.name} 대화`}>
      <ChatHeader
        roomName={room.name}
        participantSummary={waglePreviewRoomLabels[room.kind]}
        participants={participants}
        onBack={onBack}
        backLabel="대화 목록으로 돌아가기"
      />
      <div className={styles.messages} aria-label={`${room.name} 메시지 목록`}>
        {isReadOnly && serviceEvent ? (
          <ServiceActionCard
            serviceLabel={serviceEvent.source}
            title={serviceEvent.title}
            description={serviceEvent.description}
            timestamp={serviceEvent.timestamp}
            pointLabel={serviceEvent.pointLabel}
          />
        ) : (
          <>
            <DateDivider label="오늘" />
            {messages.map((message, index) => (
              <div key={message.id}>
                {index === unreadDividerIndex && <UnreadDivider />}
                <MessageBubble
                  direction={message.direction}
                  timestamp={message.timestamp}
                  readState={message.direction === 'outgoing' ? message.readState : undefined}
                  sender={room.kind === 'GROUP' ? message.sender : undefined}
                >
                  {message.text}
                </MessageBubble>
              </div>
            ))}
            {composeStatus === 'pending' && (
              <MessageBubble direction="outgoing" timestamp="지금" readState="sending">
                {draft}
              </MessageBubble>
            )}
            {composeStatus === 'failed' && (
              <div className={styles.failedRow}>
                <MessageBubble direction="outgoing" timestamp="지금" readState="failed">
                  {draft}
                </MessageBubble>
                <button type="button" className={styles.retryButton} onClick={handleRetry}>
                  재시도
                </button>
              </div>
            )}
          </>
        )}
      </div>
      {isReadOnly ? (
        <p className={styles.readOnlyNotice}>서비스 알림은 읽기 전용입니다.</p>
      ) : (
        <ChatComposer
          value={draft}
          sending={composeStatus === 'pending'}
          onChange={(value) => {
            setDraft(value);
            setComposeStatus('idle');
          }}
          onSend={handleSend}
        />
      )}
    </section>
  );
}

function WagleLandingContent() {
  const family = useFamilyContextStore((state) => state.context?.families.find((item) => item.id === state.activeFamilyId));
  // Service code is `wagle` as of migration 0007; this reads real API data,
  // so the historical code would always miss and report 'unavailable'.
  const serviceStatus = family?.services.find((service) => service.service_code === 'wagle')?.status ?? 'unavailable';
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const pushedSelectionRef = useRef(false);

  const roomIdParam = searchParams.get('room');
  const selected = waglePreviewRooms.find((room) => room.id === roomIdParam) ?? null;

  // disabled는 실제 serviceStatus에서만 파생된다 — preview 값으로 대체되지 않는다.
  const previewState = resolvePreviewPageState(searchParams.get('previewState'));
  const pageState: WaglePreviewPageState = serviceStatus !== 'active' ? 'disabled' : previewState;

  useEffect(() => {
    if (roomIdParam && !selected) {
      pushedSelectionRef.current = false;
      setSearchParams({}, { replace: true });
    }
  }, [roomIdParam, selected, setSearchParams]);

  // Desktop split view는 첫 진입 시 기본 대화가 선택된 상태가 기본이다(§3 PM 정책).
  // Mobile Room List 우선 정책은 바꾸지 않는다 — 기존 700px 분기 기준(§WagleLanding.module.css)과
  // 동일한 폭에서만 판정한다. family context가 비동기로 로드되는 동안 pageState는
  // 일시적으로 'disabled'이므로, pageState가 처음 'normal'이 되는 시점까지 기다려야
  // 한다 — didAutoSelectRef는 그 판정 기회를 정확히 1회로 고정해, 이후 사용자가
  // 목록으로 돌아가는 의도적 조작을 덮어쓰지 않는다.
  const didAutoSelectRef = useRef(false);
  useEffect(() => {
    if (didAutoSelectRef.current) return;
    if (pageState !== 'normal') return;
    didAutoSelectRef.current = true;
    if (searchParams.get('room')) return;
    if (!window.matchMedia('(min-width: 701px)').matches) return;
    const [firstRoom] = waglePreviewRooms;
    if (firstRoom) setSearchParams({ room: firstRoom.id }, { replace: true });
  }, [pageState, searchParams, setSearchParams]);

  const selectRoom = (id: string) => {
    if (selected) {
      setSearchParams({ room: id }, { replace: true });
    } else {
      setSearchParams({ room: id });
      pushedSelectionRef.current = true;
    }
  };

  const handleBack = () => {
    if (pushedSelectionRef.current) {
      pushedSelectionRef.current = false;
      navigate(-1);
    } else {
      setSearchParams({}, { replace: true });
    }
  };

  if (pageState === 'disabled') {
    return (
      <div className={styles.pageState}>
        <EmptyState
          title="와글와글을 사용할 수 없어요"
          description="가족의 와글와글 서비스 상태를 확인한 뒤 다시 시도해주세요."
        />
      </div>
    );
  }

  if (pageState === 'loading') {
    return (
      <div className={styles.pageState}>
        <LoadingState label="대화방을 불러오는 중" minHeight={320} />
      </div>
    );
  }

  if (pageState === 'empty') {
    return (
      <div className={styles.pageState}>
        <EmptyState title="아직 대화방이 없어요" description="가족과의 대화가 시작되면 이곳에 표시됩니다." />
      </div>
    );
  }

  if (pageState === 'error') {
    return (
      <div className={styles.pageState}>
        <ErrorState
          title="와글와글을 불러오지 못했어요"
          description="잠시 후 다시 시도해주세요."
          onRetry={() => setSearchParams({}, { replace: true })}
        />
      </div>
    );
  }

  return (
    <section className={styles.waglePage} aria-labelledby="wagle-title">
      <aside className={`${styles.roomList} ${selected ? styles.roomListHiddenMobile : ''}`}>
        <header className={styles.roomListHeader}>
          <p className={styles.eyebrow}>몽글 · 가족 대화</p>
          <h1 id="wagle-title">와글와글</h1>
          <p className={styles.roomListDescription}>가족과 서비스 소식을 한곳에서 확인하세요.</p>
        </header>
        <div className={styles.roomItems} role="list" aria-label="대화방 목록">
          {waglePreviewRooms.map((room) => (
            <div role="listitem" key={room.id}>
              <RoomItem
                kind={room.kind}
                title={room.name}
                preview={room.preview}
                activityLabel={room.time}
                unreadCount={room.unread}
                selected={selected?.id === room.id}
                onSelect={() => selectRoom(room.id)}
              />
            </div>
          ))}
        </div>
        {import.meta.env.DEV && (
          <p className={styles.previewNotice}>UX Gate 미리보기 · 실제 API 연결 전 화면입니다.</p>
        )}
      </aside>
      <div className={`${styles.roomPane} ${!selected ? styles.roomPaneEmptyMobile : ''}`}>
        {selected ? (
          <Conversation room={selected} onBack={handleBack} />
        ) : (
          <div className={styles.noSelection}>
            <Avatar alt="와글와글" fallback="와" size={44} className={styles.noSelectionAvatar} />
            <h2>대화방을 선택하세요</h2>
            <p>개인 대화, 가족 그룹, 서비스 알림을 확인할 수 있습니다.</p>
          </div>
        )}
      </div>
    </section>
  );
}


/**
 * MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001.
 *
 * Two Wave 3 concerns wrap the screen without changing what it renders:
 *
 * 1. **Device screen lock.** The gate covers this screen only — the Account
 *    Session, Markpoint, the Family screens and Push all keep working behind
 *    it, which is contract, not an accident of placement.
 * 2. **Realtime connection.** The socket is opened here so the connection
 *    state is real and observable. It subscribes to no rooms yet: this screen
 *    still renders preview fixtures rather than API rooms, so there are no real
 *    room ids to subscribe to. Wiring those is `MONGLE-W5-TARGET-UI-001`
 *    (Wave 6), whose own Start Gate forbids claiming integration while
 *    rendering from fixtures. Reported rather than papered over.
 */
export function WagleLanding() {
  const navigate = useNavigate();
  const { state } = useWagleRealtime({ rooms: [] });

  return (
    <WaglePinLock onLeave={() => navigate('/dashboard')}>
      <div data-wagle-realtime-state={state}>
        <WagleLandingContent />
      </div>
    </WaglePinLock>
  );
}
