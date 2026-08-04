import styles from './ParentDashboardScreen.module.css';
import type { ParentDashboardProps } from './types';

export function ParentDashboardScreen({
  model,
  embedded,
  onRefresh,
  onOpenMissions,
  onSelectStatCard,
  detailPanelSlot,
  playerStatusSlot,
  balanceSlot,
  alertsSlot,
  pendingMissionSlot,
  weeklyActivitySlot,
  rankingSlot,
  overlaysSlot,
}: ParentDashboardProps) {
  return (
    <main className={`${styles.page} ${embedded ? styles.embedded : ''}`} data-canonical-screen-id="2i" data-canonical-screen-label="보호자 대시보드" data-canonical-source="wave7-full-authority">
      {!embedded && (
        <aside>
          <b>몽글</b>
          {['대시보드', '미션 관리', '포인트 관리', '사용자 관리', '알림 관리', '설정'].map((name, index) => (
            <button key={name} type="button" className={index === 0 ? styles.active : ''}>○ <span>{name}</span></button>
          ))}
        </aside>
      )}
      <section>
        <header>
          <div><h1>{model.title}</h1><p>우리 가족의 오늘을 확인해 보세요.</p></div>
          <div className={styles.headerActions}>
            <button type="button" className={styles.secondary} onClick={onRefresh}>새로고침</button>
            <button type="button" onClick={onOpenMissions}>🗂️ 미션 관리</button>
          </div>
        </header>

        {model.cycleLabel && (
          <div className={styles.cycleRow}>
            <span className={styles.cycleBadge}>이번 주기: {model.cycleLabel}</span>
          </div>
        )}

        <div className={styles.stats}>
          {model.statCards.map((card) => (
            <button
              type="button"
              key={card.key}
              className={`${styles.statCard} ${model.selectedStatCard === card.key ? styles.selected : ''}`}
              onClick={() => onSelectStatCard?.(card.key)}
            >
              <span>{card.label}</span>
              <b>{card.value}</b>
              {card.subtext && <small style={{ color: card.subtextColor ?? '#8a83a8' }}>{card.subtext}</small>}
            </button>
          ))}
        </div>

        {model.selectedStatCard && detailPanelSlot && (
          <div className={styles.detailPanel}>{detailPanelSlot}</div>
        )}

        <div className={styles.sections}>
          {playerStatusSlot}
          {balanceSlot}
          {alertsSlot}
          {pendingMissionSlot}
          {weeklyActivitySlot}
          {rankingSlot}
        </div>
      </section>
      {overlaysSlot}
    </main>
  );
}
