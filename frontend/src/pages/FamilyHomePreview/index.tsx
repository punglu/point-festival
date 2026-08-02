import mascot from '../../assets/logos/family-platform-mascot.png';
// Preview-local crops taken from the approved PNG (crop only, no resize) because
// no separable canonical asset for either exists anywhere in the worktree. Crop
// boxes, source SHA and result SHA are recorded in
// .../MONGLE-W6-PARALLEL-A2-FAMILY-HOME-VISUAL-DRAFT-001/final/manifest/a2-asset-crop-manifest.json
import avatarPhoto from './assets/a2-profile-avatar.png';
import bellIcon from './assets/a2-notification-bell.png';
import styles from './FamilyHomePreview.module.css';

// MONGLE-W6-PARALLEL-A2-FAMILY-HOME-MOBILE-VISUAL-001
// Presentation-only reproduction of canonical screen 1b (가족 홈). Every string,
// colour and dimension is read out of the canonical `1b` block — see
// engineering/phase2/MONGLE_W6_A2_FAMILY_HOME_MEASUREMENT.md. The OS status bar
// and the home indicator are DEVICE_CHROME and are deliberately absent; the
// gallery badge, card radius and drop shadow are GALLERY_DECORATION and are
// likewise absent. Fixtures are page-local and static: no API, no store, no
// navigation, no storage.

const activities = [
  { tone: 'star', glyph: '★', title: '민준이가 “독서 미션”을 완료했어요!', meta: '+200P 획득', point: true, time: '12분 전' },
  { tone: 'level', glyph: '↑', title: '서연이가 Lv.3 모험가가 되었어요!', meta: '레벨업 축하해요 🎉', point: false, time: '1시간 전' },
  { tone: 'gift', glyph: '♥', title: '아빠가 서연이에게 포인트를 선물했어요', meta: '+500P', point: true, time: '3시간 전' },
] as const;

// Tile icons: the canonical 1b tile markup uses emoji glyphs, but the same
// canonical source carries real inline SVGs for these three services on their
// own screens. Rule 4.2 priority 2 — reuse the canonical inline SVG rather than
// keep an emoji. Path data copied verbatim; redeclared page-local, not shared.
function CalendarIcon() { return <svg viewBox="0 0 24 24"><rect x="4" y="5.5" width="16" height="14" rx="2.5" /><path d="M8 4v3M16 4v3M4 10h16" /></svg>; }
function AlbumIcon() { return <svg viewBox="0 0 24 24"><rect x="3.6" y="5.4" width="16.8" height="13.2" rx="2.6" /><circle cx="9" cy="10.4" r="1.6" /><path d="M4.6 17.2 9.8 12l3.4 3.2 2.6-2.4 3.6 3.4" /></svg>; }
function TodoIcon() { return <svg viewBox="0 0 24 24"><rect x="5" y="4.4" width="14" height="15.2" rx="2.6" /><path d="M9 4.4V7h6V4.4" /><path d="M8.8 12.6l1.8 1.8 3.6-3.6" /></svg>; }

const services = [
  { label: '포인트 잔치', sub: '다양한 미션과 보상', active: true, Icon: null },
  { label: '가족 일정', sub: '소중한 일정을 함께', active: false, Icon: CalendarIcon },
  { label: '앨범', sub: '우리의 추억 모아보기', active: false, Icon: AlbumIcon },
  { label: '할 일', sub: '함께 목표를 관리해요', active: false, Icon: TodoIcon },
] as const;

// Path data copied verbatim from the canonical 1b dock. Redeclared here rather
// than imported from the 1c preview: the colocation contract keeps every
// preview-local part inside its own page folder.
// APPROVED_PNG_OVERRIDE: the canonical HTML strokes every dock icon
// (fill="none"). The approved PNG renders the ACTIVE item as a solid filled
// house — sampled interior (101,61,231) with a white door cut-out — so the
// active icon is filled here. Inactive icons stay stroked, as in both sources.
function HomeIcon() { return <svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M4 10.6 12 4.2l8 6.4V19a1.6 1.6 0 0 1-1.6 1.6h-3.2v-5.4H8.8v5.4H5.6A1.6 1.6 0 0 1 4 19z" /></svg>; }
function FestivalIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="M12 21c4.4-4 6.8-7.3 6.8-10.6A6.8 6.8 0 0 0 5.2 10.4C5.2 13.7 7.6 17 12 21z" /><path d="M9.6 9.6h.01M14.4 9.6h.01" /><path d="M9.9 12.6a3 3 0 0 0 4.2 0" /></svg>; }
function ChatIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="M4.4 6.4A2 2 0 0 1 6.4 4.4h11.2a2 2 0 0 1 2 2v7.2a2 2 0 0 1-2 2H9.2l-4.8 3.6z" /><path d="M8.8 10h.01M12 10h.01M15.2 10h.01" /></svg>; }
function PersonIcon() { return <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8.2" r="3.6" /><path d="M5.2 20c1.5-3.9 4-5.8 6.8-5.8s5.3 1.9 6.8 5.8" /></svg>; }

export function FamilyHomePreview() {
  const noOp = () => undefined;

  return (
    <main className={styles.page} data-implementation-mode="ui-only" data-canonical-screen-id="1b">
      <section className={styles.content}>
        <div className={styles.profile} data-visual-zone="profile">
          <div className={styles.avatarWrap}>
            <img src={avatarPhoto} alt="" className={styles.avatar} />
            <span className={styles.presence} />
          </div>
          <div className={styles.greeting}>
            <span className={styles.greetingTitle}>안녕하세요, 서연님!</span>
            <span className={styles.greetingSub}>우리 가족의 행복한 하루를 응원해요 💜</span>
          </div>
          <div className={styles.bell}><img src={bellIcon} alt="" className={styles.bellIcon} /><span className={styles.bellDot} /></div>
        </div>

        <div className={styles.hero} data-visual-zone="hero">
          <div className={styles.heroCopy}>
            <span className={styles.heroTitle}>가족 대화</span>
            <span className={styles.heroBody}>지금 가족들과<br />이야기 나눠보세요</span>
            <button type="button" className={styles.heroCta} onClick={noOp}>바로가기 <b>›</b></button>
          </div>
          <img src={mascot} alt="" className={styles.heroMascot} />
          <div className={styles.typing}><i /><i /><i /></div>
        </div>

        <div className={styles.activity} data-visual-zone="activity">
          <div className={styles.activityHead}>
            <span className={styles.activityTitle}>가족 최근 활동</span>
            <button type="button" className={styles.activityMore} onClick={noOp}>더보기 ›</button>
          </div>
          {activities.map((activity, index) => (
            <div
              key={activity.title}
              data-visual-zone="activity-row"
              className={index < activities.length - 1 ? `${styles.activityRow} ${styles.activityDivider}` : styles.activityRow}
            >
              <div className={`${styles.activityIcon} ${styles[activity.tone]}`}>{activity.glyph}</div>
              <div className={styles.activityCopy}>
                <span className={styles.activityName}>{activity.title}</span>
                <span className={activity.point ? styles.activityPoint : styles.activityMeta}>{activity.meta}</span>
              </div>
              <span className={styles.activityTime}>{activity.time}</span>
            </div>
          ))}
        </div>

        <div className={styles.services} data-visual-zone="services">
          <span className={styles.servicesTitle}>우리 서비스</span>
          <div className={styles.tileGrid}>
            {services.map((service) => (
              <button
                type="button"
                key={service.label}
                onClick={noOp}
                data-visual-zone="service-tile"
                className={service.active ? `${styles.tile} ${styles.tileActive}` : styles.tile}
              >
                {!service.active && <span className={styles.tileBadge}>준비중</span>}
                {service.active
                  ? <img src={mascot} alt="" className={styles.tileImage} />
                  : <span className={styles.tileGlyph}>{service.Icon && <service.Icon />}</span>}
                <span className={styles.tileLabel}>{service.label}</span>
                <span className={styles.tileSub}>{service.sub}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <nav className={styles.dock} data-visual-zone="dock" aria-label="미리보기 하단 메뉴">
        <button type="button" className={styles.dockActive} onClick={noOp}><HomeIcon /><span>홈</span></button>
        <button type="button" onClick={noOp}><FestivalIcon /><span>포인트 잔치</span></button>
        <button type="button" onClick={noOp}><ChatIcon /><span>대화</span></button>
        <button type="button" onClick={noOp}><PersonIcon /><span>나</span></button>
      </nav>
    </main>
  );
}
