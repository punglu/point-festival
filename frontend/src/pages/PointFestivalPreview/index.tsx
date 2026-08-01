import { useState } from 'react';
import mascot from '../../assets/logos/family-platform-mascot.png';
import styles from './PointFestivalPreview.module.css';

const days = [
  ['월', '20'], ['화', '21'], ['수', '22'], ['목', '23'], ['금', '24'], ['토', '25'], ['일', '26'],
];

const missions = [
  { icon: '🧹', iconClass: 'clean', title: '방 청소하기', subtitle: '내 방을 깨끗하게 정리해요', reward: '+40P', status: '완료', progress: '100%', count: '1/1', kind: 'complete' },
  { icon: '📖', iconClass: 'study', title: '숙제 다 하기', subtitle: '오늘의 숙제를 모두 완료해요', reward: '+40P', status: '진행 중', action: '바로가기', progress: '60%', count: '3/5', kind: 'progress' },
  { icon: '👥', iconClass: 'kind', title: '동생과 사이좋게', subtitle: '동생에게 친절하게 대해요', reward: '+40P', status: '승인 대기', action: '바로가기', progress: '0%', count: '0/1', kind: 'pending' },
];

function HomeIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="M4 10.6 12 4.2l8 6.4V19a1.6 1.6 0 0 1-1.6 1.6h-3.2v-5.4H8.8v5.4H5.6A1.6 1.6 0 0 1 4 19z" /></svg>; }
function FestivalIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="M12 21c4.4-4 6.8-7.3 6.8-10.6A6.8 6.8 0 0 0 5.2 10.4C5.2 13.7 7.6 17 12 21z" /><path d="M9.6 9.6h.01M14.4 9.6h.01" /><path d="M9.9 12.6a3 3 0 0 0 4.2 0" /></svg>; }
function ChatIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="M4.4 6.4A2 2 0 0 1 6.4 4.4h11.2a2 2 0 0 1 2 2v7.2a2 2 0 0 1-2 2H9.2l-4.8 3.6z" /><path d="M8.8 10h.01M12 10h.01M15.2 10h.01" /></svg>; }
function PersonIcon() { return <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8.2" r="3.6" /><path d="M5.2 20c1.5-3.9 4-5.8 6.8-5.8s5.3 1.9 6.8 5.8" /></svg>; }

export function PointFestivalPreview() {
  const [selectedDay, setSelectedDay] = useState('22');
  const noOp = () => undefined;

  return (
    <main className={styles.page} data-implementation-mode="ui-only" data-canonical-screen-id="1c">
      <section className={styles.content}>
        <header className={styles.header} data-visual-zone="header">
          <img src={mascot} alt="" className={styles.logo} />
          <div className={styles.headerCopy}><h1>포인트 잔치</h1><p>미션을 완료하고 포인트를 모아봐요</p></div>
          <button type="button" className={styles.logout} onClick={noOp}>↪ 로그아웃</button>
        </header>

        <section className={styles.profileCard} data-visual-zone="profile">
          <div className={styles.profileTop}>
            <div className={styles.avatar}>서</div>
            <div className={styles.levelInfo}><div><strong>서연</strong><span className={styles.level}>Lv.3</span></div><div className={styles.track} data-visual-zone="profile-progress"><i /></div></div>
            <div className={styles.points}><strong>320P <em>/ 500P</em></strong><span>다음 레벨까지 180P 남았어요</span></div>
          </div>
          <div className={styles.metrics}>
            <div><span>오늘 획득</span><strong>40P</strong></div><div><span>남은 미션</span><strong className={styles.darkMetric}>2개</strong></div><div><span>현재 보유</span><strong>320P</strong></div>
          </div>
        </section>

        <section className={styles.weekCard} data-visual-zone="week-picker"><span className={styles.weekTitle}>7월 3주차 <b>›</b></span><div className={styles.days}>{days.map(([weekday, day]) => <button type="button" key={day} className={selectedDay === day ? styles.selectedDay : ''} onClick={() => setSelectedDay(day)}><span>{weekday}</span><i>{day}</i></button>)}</div></section>

        <section className={styles.surface} data-visual-zone="cheers"><h2>가족 응원 메시지</h2><div className={styles.cheers}>
          <article><i className={styles.mom}>엄마</i><div><p>서연아, 오늘도 힘내!<br />너라면 잘할 수 있어 💜</p><span>1시간 전</span></div></article>
          <article><i className={styles.dad}>아빠</i><div><p>미션 하나씩 해내는 모습이<br />정말 멋져요! 👍</p><span>3시간 전</span></div></article>
        </div></section>

        <section className={styles.surface} data-visual-zone="missions"><h2>오늘의 미션</h2><div className={styles.missions}>{missions.map((mission) => <button type="button" className={styles.mission} key={mission.title} onClick={noOp} data-visual-zone="mission-row">
          <span className={styles.missionMain}><span className={`${styles.missionIcon} ${styles[mission.iconClass]}`}>{mission.icon}</span><span className={styles.missionCopy} data-visual-zone="mission-copy"><strong>{mission.title}</strong><small>{mission.subtitle}</small></span><strong className={styles.reward}>{mission.reward}</strong><span className={`${styles.status} ${styles[mission.kind]}`}>{mission.status}</span>{mission.action && <span className={styles.action}>{mission.action}</span>}</span>
          <span className={styles.missionProgress}><span className={styles.progressLine}><i style={{ width: mission.progress }} /></span><small className={styles.progressCount}>{mission.count}</small></span>
        </button>)}</div>
          <button type="button" className={styles.historyRow} onClick={noOp}><span className={`${styles.missionIcon} ${styles.historyIcon}`}>💳</span><span className={styles.missionCopy}><strong>포인트 사용 내역</strong><small>문구점에서 노트 구입</small></span><span className={styles.historyAmount}><strong>−30P</strong><small>어제 17:30</small></span></button>
        </section>
      </section>
      <nav className={styles.dock} aria-label="미리보기 하단 메뉴"><button type="button" onClick={noOp}><HomeIcon /><span>홈</span></button><button type="button" className={styles.activeDock} onClick={noOp}><FestivalIcon /><span>포인트 잔치</span></button><button type="button" onClick={noOp}><ChatIcon /><span>대화</span></button><button type="button" onClick={noOp}><PersonIcon /><span>나</span></button></nav>
    </main>
  );
}
