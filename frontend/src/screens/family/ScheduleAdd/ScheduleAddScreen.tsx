import styles from './ScheduleAddScreen.module.css';
import type { ScheduleAddProps } from './types';

export function ScheduleAddScreen({ model, onBack, onSave, onChangeField, onToggleAttendee }: ScheduleAddProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1o">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>일정 추가</h1>
        <button type="button" onClick={onSave}>저장</button>
      </header>
      <form className={styles.form} onSubmit={(e) => e.preventDefault()}>
        <label>
          일정 제목
          <input value={model.title} onChange={(e) => onChangeField?.('title', e.target.value)} />
        </label>
        <label>
          날짜와 시간
          <div>
            <input value={model.date} onChange={(e) => onChangeField?.('date', e.target.value)} />
            <input value={model.time} onChange={(e) => onChangeField?.('time', e.target.value)} />
          </div>
        </label>
        <label>
          장소
          <input value={model.place} onChange={(e) => onChangeField?.('place', e.target.value)} />
        </label>
        <label>
          참석자
          <div className={styles.people}>
            {model.attendees.map((a) => (
              <button type="button" key={a.name} onClick={() => onToggleAttendee?.(a.name)}>
                {a.name} {a.selected ? '✓' : ''}
              </button>
            ))}
          </div>
        </label>
        <label>
          알림
          <select value={model.reminder} onChange={(e) => onChangeField?.('reminder', e.target.value)}>
            <option>10분 전</option>
            <option>30분 전</option>
            <option>1시간 전</option>
          </select>
        </label>
        <label>
          메모
          <textarea value={model.memo} onChange={(e) => onChangeField?.('memo', e.target.value)} />
        </label>
        <aside>▣ 일정은 가족 모두에게 알림으로 전달돼요.</aside>
      </form>
    </main>
  );
}
