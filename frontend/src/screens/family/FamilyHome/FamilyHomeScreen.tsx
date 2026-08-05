import mascot from '../../../assets/logos/family-platform-mascot.png';
import avatarPhoto from './assets/a2-profile-avatar.png';
import bellIcon from './assets/a2-notification-bell.png';
import styles from './FamilyHomeScreen.module.css';
import type { FamilyHomeScreenProps, FamilyHomeServiceIcon } from './types';

// Path data copied verbatim from the canonical 1b tile markup — the same 3
// inline SVGs the original FamilyHomePreview declared page-local. Rule 4.2
// priority 2: reuse the canonical inline SVG rather than an emoji.
function CalendarIcon() { return <svg viewBox="0 0 24 24"><rect x="4" y="5.5" width="16" height="14" rx="2.5" /><path d="M8 4v3M16 4v3M4 10h16" /></svg>; }
function AlbumIcon() { return <svg viewBox="0 0 24 24"><rect x="3.6" y="5.4" width="16.8" height="13.2" rx="2.6" /><circle cx="9" cy="10.4" r="1.6" /><path d="M4.6 17.2 9.8 12l3.4 3.2 2.6-2.4 3.6 3.4" /></svg>; }
function TodoIcon() { return <svg viewBox="0 0 24 24"><rect x="5" y="4.4" width="14" height="15.2" rx="2.6" /><path d="M9 4.4V7h6V4.4" /><path d="M8.8 12.6l1.8 1.8 3.6-3.6" /></svg>; }

const TILE_ICON: Record<FamilyHomeServiceIcon, (() => JSX.Element) | null> = {
  markpoint: null, // active tile uses the mascot image, not an SVG glyph — see below
  schedule: CalendarIcon,
  album: AlbumIcon,
  todo: TodoIcon,
};

export function FamilyHomeScreen({ model, onHeroClick, onActivityMore, onServiceClick, onBellClick }: FamilyHomeScreenProps) {
  return (
    <section className={styles.screen} data-canonical-screen-id="1b" data-canonical-screen-label="가족 홈" data-canonical-source="wave6-a2-family-home">
      <div className={styles.profile} data-visual-zone="profile">
        <div className={styles.avatarWrap}>
          <img src={avatarPhoto} alt="" className={styles.avatar} />
          <span className={styles.presence} />
        </div>
        <div className={styles.greeting}>
          <span className={styles.greetingTitle}>{model.greetingTitle}</span>
          <span className={styles.greetingSub}>{model.greetingSub}</span>
        </div>
        <button type="button" className={styles.bell} onClick={onBellClick} aria-label="알림">
          <img src={bellIcon} alt="" className={styles.bellIcon} />
          {model.bellUnread && <span className={styles.bellDot} />}
        </button>
      </div>

      <div className={styles.hero} data-visual-zone="hero">
        <div className={styles.heroCopy}>
          <span className={styles.heroTitle}>{model.heroTitle}</span>
          <span className={styles.heroBody}>
            {model.heroBody.map((line, index) => (
              <span key={line}>
                {line}
                {index < model.heroBody.length - 1 && <br />}
              </span>
            ))}
          </span>
          <button type="button" className={styles.heroCta} onClick={onHeroClick}>{model.heroCtaLabel} <b>›</b></button>
        </div>
        <img src={mascot} alt="" className={styles.heroMascot} />
        <div className={styles.typing}><i /><i /><i /></div>
      </div>

      <div className={styles.activity} data-visual-zone="activity">
        <div className={styles.activityHead}>
          <span className={styles.activityTitle}>{model.activitiesTitle}</span>
          <button type="button" className={styles.activityMore} onClick={onActivityMore}>{model.activitiesMoreLabel} ›</button>
        </div>
        {model.activities.length === 0 && <p className={styles.activityEmpty}>아직 활동이 없어요.</p>}
        {model.activities.map((activity, index) => (
          <div
            key={`${activity.title}-${activity.time}`}
            data-visual-zone="activity-row"
            className={index < model.activities.length - 1 ? `${styles.activityRow} ${styles.activityDivider}` : styles.activityRow}
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
        <span className={styles.servicesTitle}>{model.servicesTitle}</span>
        <div className={styles.tileGrid}>
          {model.services.map((service) => {
            const Icon = TILE_ICON[service.icon];
            return (
              <button
                type="button"
                key={service.id}
                onClick={() => onServiceClick?.(service.id)}
                data-visual-zone="service-tile"
                data-testid={`family-home-tile-${service.id}`}
                className={service.highlighted ? `${styles.tile} ${styles.tileActive}` : styles.tile}
              >
                {!service.available && <span className={styles.tileBadge}>준비중</span>}
                {service.highlighted
                  ? <img src={mascot} alt="" className={styles.tileImage} />
                  : <span className={styles.tileGlyph}>{Icon && <Icon />}</span>}
                <span className={styles.tileLabel}>{service.label}</span>
                <span className={styles.tileSub}>{service.sub}</span>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
