import pinLogo from '../../assets/logos/family-platform-mascot.png';
import minjunAvatar from './assets/minjun-avatar.png';
import seoyeonAvatar from './assets/seoyeon-avatar.png';
import styles from './AdminPointManagementPreview.module.css';

type IconName = 'home' | 'calendar' | 'points' | 'users' | 'user' | 'bell' | 'settings' | 'filter' | 'trendDown' | 'chevronDown' | 'edit' | 'trash';

const iconPaths: Record<IconName, React.ReactNode> = {
  home: <path d="M4 10.6 12 4.2l8 6.4V19a1.6 1.6 0 0 1-1.6 1.6h-3.2v-5.4H8.8v5.4H5.6A1.6 1.6 0 0 1 4 19z" />,
  calendar: <><rect x="4" y="5.5" width="16" height="14" rx="2.5" /><path d="M8 4v3M16 4v3M4 10h16" /></>,
  points: <><ellipse cx="12" cy="6.5" rx="7" ry="2.8" /><path d="M5 6.5v11c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-11" /><path d="M5 12c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8" /></>,
  users: <><circle cx="9.5" cy="8.5" r="3.2" /><path d="M3.6 19c1.3-3.4 3.5-5 5.9-5s4.6 1.6 5.9 5" /><path d="M16.2 6.2a3 3 0 0 1 0 5.8M17.6 14.4c1.4.8 2.4 2.3 3 4.6" /></>,
  user: <><circle cx="12" cy="8" r="3.5" /><path d="M5.6 20c1.4-3.8 3.6-5.7 6.4-5.7s5 1.9 6.4 5.7" /></>,
  bell: <><path d="M6.5 10a5.5 5.5 0 0 1 11 0c0 4 1.3 5.4 1.7 5.9H4.8c.4-.5 1.7-1.9 1.7-5.9z" /><path d="M10.2 19a2 2 0 0 0 3.6 0" /></>,
  settings: <><circle cx="12" cy="12" r="3" /><path d="M12 3.5v2.4M12 18.1v2.4M4.9 7.9l2 1.2M17.1 14.9l2 1.2M19.1 7.9l-2 1.2M6.9 14.9l2 1.2" /></>,
  filter: <path d="M4 5h16l-6.2 7.1v5.1L10 19v-6.9z" />,
  trendDown: <><path d="m5 7 5.1 5.1 3.5-3.5 5.5 5.5" /><path d="M19.1 10.7v3.9h-3.9" /></>,
  chevronDown: <path d="M5 9l7 7 7-7" />,
  edit: <><path d="m14.6 5.3 4.1 4.1M5 19l3.2-.6 9.8-9.8-2.6-2.6-9.8 9.8z" /><path d="M4 21h16" /></>,
  trash: <><path d="M4.5 7h15M9.5 7V4.8h5V7M7.2 7l.9 13h7.8l.9-13M10 11v5M14 11v5" /></>,
};

function Icon({ name, size = 21, stroke = 1.8 }: { name: IconName; size?: number; stroke?: number }) {
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round">{iconPaths[name]}</svg>;
}

const navItems: Array<{ icon: IconName; label: string; active?: boolean }> = [
  { icon: 'home', label: '대시보드' }, { icon: 'calendar', label: '미션 관리' }, { icon: 'points', label: '포인트 관리', active: true },
  { icon: 'users', label: '사용자 관리' }, { icon: 'bell', label: '알림 관리' }, { icon: 'settings', label: '설정' },
];

const ledgerRows = [
  ['서연', '젤리 간식 교환', '−30P', '18:25', '엄마', 'seoyeon'],
  ['민준', '게임 이용 시간 초과', '−20P', '17:10', '아빠', 'minjun'],
  ['서연', '미션 실패', '−10P', '16:50', '엄마', 'seoyeon'],
  ['민준', '정리 정돈 미실시', '−10P', '16:20', '아빠', 'minjun'],
  ['서연', '약속 시간 지연', '−10P', '15:40', '엄마', 'seoyeon'],
];

const noOp = (event: React.MouseEvent<HTMLElement>) => event.preventDefault();

export function AdminPointManagementPreview() {
  return (
    <div className={styles.previewViewport} data-implementation-mode="ui-only" data-canonical-screen-id="1e">
      <div className={styles.frame}>
        <aside className={styles.sidebar}>
          <div className={styles.brand}>
            <img className={styles.logo} src={pinLogo} alt="" />
            <strong>우리 가족</strong><span>관리자 모드</span>
          </div>
          <nav className={styles.nav} aria-label="관리자 메뉴">
            {navItems.map(({ icon, label, active }) => <a className={`${styles.navItem} ${active ? styles.navItemActive : ''}`} href="#" onClick={noOp} key={label}><Icon name={icon} />{label}</a>)}
          </nav>
          <div className={styles.accountFooter}>
            <span className={styles.adminAvatar}><Icon name="user" size={21} /></span><span className={styles.accountText}><strong>관리자</strong><small>admin@ourfamily.com</small></span><span className={styles.footerChevron}><Icon name="chevronDown" size={12} stroke={2.4} /></span>
          </div>
        </aside>
        <main className={styles.main}>
          <header className={styles.header}>
            <div className={styles.heading}><h1>포인트 관리</h1><p>포인트 차감 내역을 조회하고 관리할 수 있습니다.</p></div>
            <div className={styles.headerActions}><button className={styles.dateButton} type="button" onClick={noOp}><Icon name="calendar" size={19} /><span>2026. 07. 22 (수)</span></button><button className={styles.addButton} type="button" onClick={noOp}>＋ 차감 추가</button></div>
          </header>
          <section className={styles.filters} aria-label="포인트 필터"><div className={styles.filterTabs}><button className={styles.tabActive} type="button" onClick={noOp}>전체</button><button type="button" onClick={noOp}>서연</button><button type="button" onClick={noOp}>민준</button></div><button className={styles.filterButton} type="button" onClick={noOp}><Icon name="filter" size={14} />전체 필터 <Icon name="chevronDown" size={11} stroke={2.4} /></button></section>
          <section className={styles.stats} aria-label="포인트 현황">
            <StatCard avatar={seoyeonAvatar} name="서연 오늘 보유" value="320" tone="purple" />
            <StatCard avatar={minjunAvatar} name="민준 오늘 보유" value="180" tone="green" />
            <StatCard avatar="trendDown" name="오늘 총 차감" value="−30" tone="red" />
          </section>
          <section className={styles.tableCard} aria-label="포인트 차감 내역">
            <div className={`${styles.tableRow} ${styles.tableHeader}`}><span>사용자</span><span>사유</span><span>금액</span><span>일시</span><span>등록자</span><span>관리</span></div>
            {ledgerRows.map(([user, reason, amount, time, author, tone]) => <div className={styles.tableRow} key={`${user}-${time}`}><span className={styles.userCell}><i className={tone === 'minjun' ? styles.mj : styles.sy}><img src={tone === 'minjun' ? minjunAvatar : seoyeonAvatar} alt="" /></i>{user}</span><span>{reason}</span><strong className={styles.negative}>{amount}</strong><span className={styles.muted}>{time}</span><span className={styles.muted}>{author}</span><span className={styles.rowActions}><button type="button" aria-label={`${user} 내역 수정`} onClick={noOp}><Icon name="edit" size={15} /></button><button type="button" aria-label={`${user} 내역 삭제`} onClick={noOp}><Icon name="trash" size={15} /></button></span></div>)}
            <div className={styles.pagination}><span>총 25건</span><div><button type="button" onClick={noOp}>‹</button><button className={styles.pageActive} type="button" onClick={noOp}>1</button><button type="button" onClick={noOp}>2</button><button type="button" onClick={noOp}>3</button><button type="button" onClick={noOp}>›</button></div><button className={styles.perPage} type="button" onClick={noOp}>10개씩 <Icon name="chevronDown" size={11} stroke={2.4} /></button></div>
          </section>
          <section className={styles.infoBanner}><span className={styles.infoIcon}>ⓘ</span><div><strong>모든 포인트 차감 내역은 기록으로 남습니다.</strong><p>내역 수정 및 삭제는 기록에 보관되며, 투명한 포인트 관리를 지원합니다.</p></div></section>
        </main>
      </div>
    </div>
  );
}

function StatCard({ avatar, name, value, tone }: { avatar: string; name: string; value: string; tone: 'purple' | 'green' | 'red' }) {
  return <article className={styles.statCard}><span className={`${styles.statAvatar} ${styles[tone]}`}>{tone === 'red' ? <Icon name="trendDown" size={34} stroke={2.6} /> : <img src={avatar} alt="" />}</span><span><small>{name}</small><strong>{value}<em>P</em></strong></span></article>;
}
