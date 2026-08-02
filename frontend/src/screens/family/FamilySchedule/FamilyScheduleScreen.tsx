import styles from './FamilyScheduleScreen.module.css';
import type { FamilyScheduleProps, ScheduleEvent } from './types';

function Event({ event, onSelect }: { event: ScheduleEvent; onSelect?: (event: ScheduleEvent) => void }) {
  return (
    <button type="button" className={styles.event} onClick={() => onSelect?.(event)}>
      <i className={styles[event.color]} />
      <div><b>{event.title}</b><span>{event.meta}</span></div>
      <em>{event.people.map((name) => <i key={name}>{name}</i>)}</em>
    </button>
  );
}

export function FamilyScheduleScreen({ model, onBack, onAddSchedule, onSelectEvent }: FamilyScheduleProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1g">
      <section className={styles.content}>
        <header>
          <button type="button" onClick={onBack}>←</button>
          <div><h1>가족 일정</h1><span>{model.weekSummary}</span></div>
          <button type="button" className={styles.add} onClick={onAddSchedule}>＋ 일정 추가</button>
        </header>
        <section className={styles.calendar}>
          <div className={styles.month}><b>{model.monthLabel}</b><span>‹ <strong>오늘</strong> ›</span></div>
          <div className={styles.week}>{model.weekdays.map((day) => <span key={day}>{day}</span>)}</div>
          <div className={styles.days}>
            {model.days.map((d, index) => (
              <div key={`${d.day}-${index}`}>
                <b className={d.marker === 'active' ? styles.today : ''}>{d.day}</b>
                <i className={styles[d.marker] ?? styles.empty} />
              </div>
            ))}
          </div>
          <div className={styles.legend}>
            <span><i className={styles.purple} />가족 행사</span>
            <span><i className={styles.green} />학교/학원</span>
            <span><i className={styles.yellow} />기념일</span>
          </div>
        </section>
        <section className={styles.schedule}>
          <div className={styles.scheduleHead}><b>{model.todayLabel}</b><span>{model.todayEvents.length}개</span></div>
          {model.todayEvents.map((e) => <Event key={e.id} event={e} onSelect={onSelectEvent} />)}
        </section>
        <section className={styles.upcoming}>
          <div className={styles.scheduleHead}><b>다가오는 일정</b><span>전체 보기 ›</span></div>
          {model.upcomingEvents.map((e) => <Event key={e.id} event={e} onSelect={onSelectEvent} />)}
        </section>
        <aside className={styles.notice}>
          <span>▣</span>
          <div><b>일정은 가족 모두에게 알림으로 전달돼요.</b><small>참석자를 지정하면 해당 구성원에게만 알립니다.</small></div>
        </aside>
      </section>
    </main>
  );
}
