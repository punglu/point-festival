import mascot from '../../../assets/logos/family-platform-mascot.png';
import styles from './PointFestivalScreen.module.css';
import type { PointFestivalScreenProps } from './types';

const MISSION_ICON = '📌';

export function PointFestivalScreen({
  model,
  showWeeklySection = true,
  onLogout,
  onSelectDay,
  onSelectMission,
  onHistoryClick,
}: PointFestivalScreenProps) {
  const days = model.days ?? [];
  const missions = model.missions ?? [];

  return (
    <main className={styles.screen} data-canonical-screen-id="1c" data-canonical-screen-label="포인트 잔치" data-canonical-source="wave6-point-festival">
      <section className={styles.content}>
        <header className={styles.header} data-visual-zone="header">
          <img src={mascot} alt="" className={styles.logo} />
          <div className={styles.headerCopy}><h1>포인트 잔치</h1><p>미션을 완료하고 포인트를 모아봐요</p></div>
          <button type="button" className={styles.logout} onClick={onLogout}>↪ 로그아웃</button>
        </header>

        <section className={styles.profileCard} data-visual-zone="profile">
          <div className={styles.profileTop}>
            <div className={styles.avatar}>{model.playerName.slice(0, 1)}</div>
            <div className={styles.levelInfo}>
              <div><strong>{model.playerName}</strong><span className={styles.level} data-testid="markpoint-level">Lv.{model.level}</span></div>
              <div className={styles.track} data-visual-zone="profile-progress"><i style={{ width: `${model.levelProgressPercent}%` }} /></div>
            </div>
            <div className={styles.points}><strong>{model.earnedLabel}</strong><span>{model.levelHint}</span></div>
          </div>
          <div className={styles.metrics}>
            <div><span>오늘 획득</span><strong>{model.todayEarned}P</strong></div>
            <div><span>남은 미션</span><strong className={styles.darkMetric}><span data-testid="markpoint-remaining">{model.remainingMissions}</span>개</strong></div>
            <div><span>현재 보유</span><strong><span data-testid="markpoint-balance">{model.currentBalance}</span>P</strong></div>
          </div>
        </section>

        {showWeeklySection && (
          <>
            <section className={styles.weekCard} data-visual-zone="week-picker">
              <span className={styles.weekTitle}>{model.weekLabel}</span>
              <div className={styles.days}>
                {days.map((day) => (
                  <button
                    type="button"
                    key={day.date}
                    className={day.date === model.selectedDate ? styles.selectedDay : ''}
                    onClick={() => onSelectDay?.(day.date)}
                    data-testid={`point-festival-day-${day.date}`}
                  >
                    <span>{day.weekday}</span><i>{day.day}</i>
                  </button>
                ))}
              </div>
            </section>

            {model.cheerMessages && model.cheerMessages.length > 0 && (
              <section className={styles.surface} data-visual-zone="cheers">
                <h2>가족 응원 메시지</h2>
                <div className={styles.cheers}>
                  {model.cheerMessages.map((cheer) => (
                    <article key={cheer.name}>
                      <i className={styles[cheer.tone] ?? undefined}>{cheer.name}</i>
                      <div><p>{cheer.message}</p><span>{cheer.time}</span></div>
                    </article>
                  ))}
                </div>
              </section>
            )}

            <section className={styles.surface} data-visual-zone="missions">
              <h2>{model.missionsTitle}</h2>
              <div className={styles.missions}>
                {missions.length === 0 && <p className={styles.missionsEmpty}>이 날은 배정된 미션이 없어요.</p>}
                {missions.map((mission) => (
                  <button
                    type="button"
                    className={styles.mission}
                    key={mission.id}
                    onClick={() => onSelectMission?.(mission.id)}
                    data-visual-zone="mission-row"
                    data-testid={`point-festival-mission-${mission.id}`}
                  >
                    <span className={styles.missionMain}>
                      <span className={`${styles.missionIcon} ${styles.study}`}>{MISSION_ICON}</span>
                      <span className={styles.missionCopy} data-visual-zone="mission-copy"><strong>{mission.title}</strong><small>{mission.subtitle}</small></span>
                      <strong className={styles.reward}>{mission.reward}</strong>
                      <span className={`${styles.status} ${styles[mission.statusKind]}`}>{mission.status}</span>
                      {mission.action && <span className={styles.action}>{mission.action}</span>}
                    </span>
                    {mission.progress && mission.count && (
                      <span className={styles.missionProgress}>
                        <span className={styles.progressLine}><i style={{ width: mission.progress }} /></span>
                        <small className={styles.progressCount}>{mission.count}</small>
                      </span>
                    )}
                  </button>
                ))}
              </div>
              {model.historyEntry && (
                <button type="button" className={styles.historyRow} onClick={onHistoryClick}>
                  <span className={`${styles.missionIcon} ${styles.historyIcon}`}>💳</span>
                  <span className={styles.missionCopy}><strong>{model.historyEntry.title}</strong><small>{model.historyEntry.subtitle}</small></span>
                  <span className={styles.historyAmount}><strong>{model.historyEntry.amount}</strong><small>{model.historyEntry.time}</small></span>
                </button>
              )}
            </section>
          </>
        )}
      </section>
    </main>
  );
}
