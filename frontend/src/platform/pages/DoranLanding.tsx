import { useState } from 'react';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './PlatformPages.module.css';

type RoomKind = 'DIRECT' | 'GROUP' | 'SERVICE';

type PreviewRoom = {
  id: string;
  kind: RoomKind;
  name: string;
  preview: string;
  time: string;
  unread?: number;
};

const previewRooms: PreviewRoom[] = [
  { id: 'direct', kind: 'DIRECT', name: '엄마', preview: '저녁 먹고 이야기해요', time: '오후 7:42', unread: 2 },
  { id: 'group', kind: 'GROUP', name: '우리 가족 주말 계획', preview: '토요일 오전에 출발하면 어때요?', time: '오후 6:18' },
  { id: 'service', kind: 'SERVICE', name: '마크포인트 알림', preview: '미션 완료 · +25 포인트', time: '오후 4:05', unread: 12 },
];

const labels: Record<RoomKind, string> = { DIRECT: '개인 대화', GROUP: '가족 그룹', SERVICE: '서비스 알림' };

function ServiceCard() {
  return <article className={styles.serviceCard} aria-label="마크포인트 서비스 알림">
    <div><span className={styles.serviceMark}>마크포인트</span><time>오늘 오후 4:05</time></div>
    <strong>미션을 완료했어요</strong>
    <p>오늘의 미션 포인트가 반영되었습니다.</p>
    <span className={styles.pointPill}>+25 포인트</span>
  </article>;
}

function Conversation({ room, onBack }: { room: PreviewRoom; onBack: () => void }) {
  const [draft, setDraft] = useState('');
  const [status, setStatus] = useState<'idle' | 'pending' | 'failed'>('idle');
  const isService = room.kind === 'SERVICE';
  const submit = () => {
    if (!draft.trim() || isService) return;
    setStatus('pending');
    window.setTimeout(() => { setStatus('failed'); }, 500);
  };
  return <section className={styles.conversation} aria-label={`${room.name} 대화`}>
    <header className={styles.roomHeader}>
      <button className={styles.backButton} onClick={onBack} aria-label="대화 목록으로 돌아가기">‹</button>
      <div><span className={styles.roomType}>{labels[room.kind]}</span><h2>{room.name}</h2></div>
    </header>
    <div className={styles.messages}>
      {isService ? <ServiceCard /> : <>
        <p className={styles.dateDivider}>오늘</p>
        <div className={styles.theirMessage}>안녕하세요! 오늘은 어땠어요?<time>오후 7:38</time></div>
        <div className={styles.myMessage}>좋았어요. 조금 뒤에 이야기해요.<time>오후 7:40</time></div>
        {status === 'pending' && <div className={styles.pendingMessage}>{draft}<small>전송 확인 중</small></div>}
        {status === 'failed' && <div className={styles.failedMessage}>{draft}<button onClick={() => setStatus('pending')}>재시도</button></div>}
      </>}
    </div>
    {isService ? <p className={styles.readOnly}>서비스 알림은 읽기 전용입니다.</p> : <form className={styles.composer} onSubmit={(event) => { event.preventDefault(); submit(); }}>
      <label className={styles.srOnly} htmlFor="doran-draft">메시지</label>
      <textarea id="doran-draft" value={draft} onChange={(event) => { setDraft(event.target.value); setStatus('idle'); }} placeholder="메시지를 입력하세요" rows={1} />
      <button type="submit" disabled={!draft.trim() || status === 'pending'}>보내기</button>
    </form>}
  </section>;
}

export function DoranLanding() {
  const family = useFamilyContextStore((state) => state.context?.families.find((item) => item.id === state.activeFamilyId));
  const serviceStatus = family?.services.find((service) => service.service_code === 'doran')?.status ?? 'unavailable';
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = previewRooms.find((room) => room.id === selectedId) ?? null;

  if (serviceStatus !== 'active') return <section className={styles.page} aria-labelledby="doran-title"><p className={styles.eyebrow}>나란 · 도란</p><h1 id="doran-title">도란을 사용할 수 없어요</h1><p>가족의 도란 서비스 상태를 확인한 뒤 다시 시도해주세요.</p><span className={styles.badge}>서비스 비활성</span></section>;

  return <section className={styles.doranPage} aria-labelledby="doran-title">
    <aside className={`${styles.roomList} ${selected ? styles.roomListHiddenMobile : ''}`}>
      <header><p className={styles.eyebrow}>나란 · 가족 대화</p><h1 id="doran-title">도란</h1><p>가족과 서비스 소식을 한곳에서 확인하세요.</p></header>
      <div className={styles.roomItems} aria-label="대화방 목록">
        {previewRooms.map((room) => <button key={room.id} className={`${styles.roomItem} ${selectedId === room.id ? styles.selectedRoom : ''}`} onClick={() => setSelectedId(room.id)}>
          <span className={styles.roomIcon} data-kind={room.kind}>{room.kind === 'DIRECT' ? '1:1' : room.kind === 'GROUP' ? '가족' : '알림'}</span>
          <span className={styles.roomMeta}><strong>{room.name}</strong><small>{labels[room.kind]}</small><em>{room.preview}</em></span>
          <span className={styles.roomActivity}><time>{room.time}</time>{room.unread && <b>{room.unread > 99 ? '99+' : room.unread}</b>}</span>
        </button>)}
      </div>
      <p className={styles.previewNotice}>UX Gate 미리보기 · 실제 API 연결 전 화면입니다.</p>
    </aside>
    <div className={`${styles.roomPane} ${!selected ? styles.roomPaneEmptyMobile : ''}`}>
      {selected ? <Conversation room={selected} onBack={() => setSelectedId(null)} /> : <div className={styles.noSelection}><span>도란</span><h2>대화방을 선택하세요</h2><p>개인 대화, 가족 그룹, 서비스 알림을 확인할 수 있습니다.</p></div>}
    </div>
  </section>;
}
