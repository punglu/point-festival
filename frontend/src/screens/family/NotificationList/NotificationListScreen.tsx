import styles from './NotificationListScreen.module.css';
import type { NotificationListProps } from './types';

export function NotificationListScreen({ model, onBack, onMarkAllRead, onFilter, onSelectNotification }: NotificationListProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1n">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <div><h1>알림</h1><span>새 알림 {model.unreadCount}개</span></div>
        <button type="button" onClick={onMarkAllRead}>모두 읽음</button>
      </header>
      <section className={styles.content}>
        <div className={styles.filters}>
          {model.filters.map((name) => (
            <button
              type="button"
              key={name}
              className={name === model.activeFilter ? styles.active : ''}
              onClick={() => onFilter?.(name)}
            >
              {name}
            </button>
          ))}
        </div>
        <h2>{model.todayLabel}</h2>
        <div className={styles.list}>
          {model.notifications.map((n) => (
            <button
              key={n.title}
              type="button"
              onClick={() => onSelectNotification?.(n)}
              className={n.unread ? styles.unread : ''}
            >
              <i>{n.icon}</i>
              <div><b>{n.title}</b><span>{n.text}</span></div>
              <time>{n.time}</time>
            </button>
          ))}
        </div>
        <aside>♧ <span>{model.footerNote}</span></aside>
      </section>
    </main>
  );
}
