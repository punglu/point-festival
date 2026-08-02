import mascot from '../../assets/logos/family-platform-mascot.png';
import type React from 'react';
import styles from './FamilyChatPreview.module.css';

type Member = '아빠' | '엄마' | '민준' | '서연';
const tone: Record<Member, string> = { 아빠: 'dad', 엄마: 'mom', 민준: 'minjun', 서연: 'seoyeon' };
const messages: Array<{ person: Member; text: React.ReactNode; time: string; mine?: boolean }> = [
  { person: '아빠', text: <>오늘 저녁은 삼겹살 어때?<br />장도 보고 올게!</>, time: '오후 6:01' },
  { person: '엄마', text: <>좋지! 나는 김치찌개 끓일게 😊<br />민준이는 상추 씻는 거 부탁해~</>, time: '오후 6:02' },
  { person: '민준', text: <>네! 알겠어요 👍</>, time: '오후 6:03' },
  { person: '서연', text: <>저는 밥할게요 🍚<br />오늘도 맛있는 저녁 기대돼요!</>, time: '오후 6:04', mine: true },
  { person: '아빠', text: <>우리 딸 든든하다~ 고마워!</>, time: '오후 6:04' },
  { person: '엄마', text: <>민준아, 방 청소는 다 했지? 😊</>, time: '오후 6:20' },
  { person: '민준', text: <>네! 방금 끝냈어요 ✨</>, time: '오후 6:21' },
];
function Avatar({ person, small = false }: { person: Member; small?: boolean }) { return <span className={`${styles.avatar} ${styles[tone[person]]} ${small ? styles.smallAvatar : ''}`}>{person}</span>; }
function DockIcon({ type }: { type: 'home' | 'festival' | 'chat' | 'person' }) {
  if (type === 'home') return <svg viewBox="0 0 24 24"><path d="M4 10.6 12 4.2l8 6.4V19a1.6 1.6 0 0 1-1.6 1.6h-3.2v-5.4H8.8v5.4H5.6A1.6 1.6 0 0 1 4 19z" /></svg>;
  if (type === 'festival') return <svg viewBox="0 0 24 24"><path d="M12 21c4.4-4 6.8-7.3 6.8-10.6A6.8 6.8 0 0 0 5.2 10.4C5.2 13.7 7.6 17 12 21z" /><path d="M9.6 9.6h.01M14.4 9.6h.01M9.9 12.6a3 3 0 0 0 4.2 0" /></svg>;
  if (type === 'chat') return <svg viewBox="0 0 24 24"><path d="M4.4 6.4A2 2 0 0 1 6.4 4.4h11.2a2 2 0 0 1 2 2v7.2a2 2 0 0 1-2 2H9.2l-4.8 3.6z" /><path d="M8.8 10h.01M12 10h.01M15.2 10h.01" /></svg>;
  return <svg viewBox="0 0 24 24"><circle cx="12" cy="8.2" r="3.6" /><path d="M5.2 20c1.5-3.9 4-5.8 6.8-5.8s5.3 1.9 6.8 5.8" /></svg>;
}
function Message({ person, text, time, mine }: { person: Member; text: React.ReactNode; time: string; mine?: boolean }) {
  return <div className={`${styles.message} ${mine ? styles.mine : ''}`}><Avatar person={person} /><div className={styles.messageContent}><b>{mine ? '서연(나)' : person}</b><div className={styles.bubbleLine}>{mine && <span className={styles.read}>읽음 3<br />{time}</span>}<p>{text}</p>{!mine && <time>{time}</time>}</div></div></div>;
}
export function FamilyChatPreview() {
  const noOp = () => undefined;
  return <main className={styles.page} data-implementation-mode="ui-only" data-canonical-screen-id="1d">
    <header className={styles.header}><button type="button" className={styles.back} onClick={noOp} aria-label="뒤로">←</button><div className={styles.roomTitle}><strong>우리 가족방</strong><span>4명 참여 중 <i /></span></div><div className={styles.participants}>{(['아빠', '엄마', '민준', '서연'] as Member[]).map((person) => <Avatar key={person} person={person} small />)}</div><div className={styles.mascot}><img src={mascot} alt="" /><i /></div></header>
    <section className={styles.thread} aria-label="가족 대화"><span className={styles.date}>7월 22일 (수)</span>{messages.slice(0, 5).map((message) => <Message key={`${message.person}-${message.time}`} {...message} />)}<div className={styles.unread}><i /><span>여기부터 안 읽음</span><i /></div>{messages.slice(5).map((message) => <Message key={`${message.person}-${message.time}`} {...message} />)}<div className={styles.albumNotice}><span className={styles.albumIcon}><svg viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="14" rx="2.5" /><circle cx="9" cy="10" r="1.4" /><path d="m5.5 17 4.3-4.5 3.2 2.8 2.2-2 3.2 3.1" /></svg></span><span>아빠님이 가족 앨범 ‘여름 여행’에 사진 3장을 추가했습니다.</span><time>오후 6:35</time></div><div className={styles.photoMessage}><Avatar person="아빠" /><div><b>아빠</b><div className={styles.photos}>{['사진 1', '사진 2', '사진 3'].map((label) => <span key={label}>{label}</span>)}</div></div><time>오후 6:36</time></div></section>
    <div className={styles.composer}><button type="button" onClick={noOp} aria-label="첨부"><svg viewBox="0 0 24 24"><path d="m8.5 12.7 5.7-5.7a3.4 3.4 0 0 1 4.8 4.8l-7.4 7.4a5 5 0 0 1-7-7L12 4.8" /></svg></button><span className={styles.camera}>⌑</span><span>메시지 입력...</span><button type="button" className={styles.send} onClick={noOp} aria-label="전송">➤</button></div>
    <nav className={styles.dock} aria-label="미리보기 하단 메뉴">{([['home', '홈'], ['festival', '포인트 잔치'], ['chat', '대화'], ['person', '나']] as const).map(([type, label]) => <button key={type} type="button" onClick={noOp} className={type === 'chat' ? styles.active : ''}><DockIcon type={type} /><span>{label}</span></button>)}</nav>
  </main>;
}
