import styles from './FamilyTodoScreen.module.css';
import type { FamilyTodoProps } from './types';

export function FamilyTodoScreen({ model, onBack, onAdd, onFilter, onToggleTodo }: FamilyTodoProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1i">
      <section className={styles.content}>
        <header>
          <button type="button" onClick={onBack}>←</button>
          <div><h1>할 일</h1><span>{model.summary}</span></div>
          <button type="button" onClick={onAdd}>＋ 할 일 추가</button>
        </header>
        <section className={styles.progress}>
          <div>
            <div><h2>오늘의 진행률</h2><span>{model.progressSubtitle}</span></div>
            <strong>{model.progressPercent}%</strong>
          </div>
          <i><b style={{ width: `${model.progressPercent}%` }} /></i>
          <footer>
            {model.counts.map((c) => <span key={c.label}>{c.label}<b>{c.value}</b></span>)}
          </footer>
        </section>
        <div className={styles.filters}>
          {model.filters.map((f) => (
            <button key={f} type="button" className={f === model.activeFilter ? styles.selected : ''} onClick={() => onFilter?.(f)}>{f}</button>
          ))}
        </div>
        <section className={styles.todoZone}>
          <header><b>오늘</b><span>{model.dateLabel}</span></header>
          <div className={styles.todoList}>
            {model.todos.map((todo) => (
              <button key={todo.id} type="button" onClick={() => onToggleTodo?.(todo)} className={todo.status === '완료' ? styles.done : ''}>
                <i>{todo.status === '완료' ? '✓' : ''}</i>
                <div><b>{todo.title}</b><span>{todo.meta}</span></div>
                <em className={todo.status === '완료' ? styles.hidden : todo.status === '지연' ? styles.late : ''}>{todo.status}</em>
              </button>
            ))}
          </div>
        </section>
        <section className={styles.goals}>
          <h2>이번 주 가족 목표</h2>
          {model.goals.map((g) => (
            <div key={g.title}>
              <span>{g.title}</span>
              <b>{g.value}</b>
              <i><em style={{ width: `${g.percent}%` }} /></i>
            </div>
          ))}
        </section>
        <aside className={styles.notice}>☑<div><b>완료한 할 일은 포인트 잔치에 반영돼요.</b><span>보호자 승인이 필요한 항목은 승인 후 지급됩니다.</span></div></aside>
      </section>
    </main>
  );
}
