import styles from './SettingsListScreen.module.css';
import type { SettingsListProps } from './types';

export function SettingsListScreen({ model, onBack, onOpenProfile, onSelectNav, onToggle, onLogout }: SettingsListProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="2k">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>설정</h1>
      </header>
      <section>
        <button type="button" className={styles.profile} onClick={onOpenProfile}>
          <i>{model.playerInitial}</i>
          <div><b>{model.playerName}</b><span>{model.playerMeta}</span></div>
          <em>›</em>
        </button>
        {model.navGroups.map((group) => (
          <div className={styles.group} key={group.title}>
            <h2>{group.title}</h2>
            <article>
              {group.items.map((item) => (
                <button key={item.key} type="button" onClick={() => onSelectNav?.(item)}>
                  <i>{item.icon}</i><span>{item.label}</span>{item.detail && <small>{item.detail}</small>}<em>›</em>
                </button>
              ))}
            </article>
          </div>
        ))}
        {model.toggleGroups.map((group) => (
          <div className={styles.group} key={group.title}>
            <h2>{group.title}</h2>
            <article>
              {group.items.map((item) => (
                <button type="button" key={item.key} className={styles.toggleRow} onClick={() => onToggle?.(item)}>
                  <i>{item.icon}</i><span>{item.label}</span><b className={item.on ? styles.on : styles.off} />
                </button>
              ))}
            </article>
          </div>
        ))}
        <button type="button" className={styles.logout} onClick={onLogout}>로그아웃</button>
        <span className={styles.version}>{model.version}</span>
      </section>
    </main>
  );
}
