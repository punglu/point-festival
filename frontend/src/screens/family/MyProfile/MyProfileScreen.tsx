import styles from './MyProfileScreen.module.css';
import type { MyProfileListItem, MyProfileProps } from './types';

function Glyph({ kind }: { kind: string }) {
  return (
    <svg viewBox="0 0 24 24">
      {kind === 'list' && <path d="M5 6.5h14M5 12h14M5 17.5h9" />}
      {kind === 'check' && <path d="M5 12.6l4 4 10-10" />}
      {kind === 'star' && <path d="m12 4.5 2.3 4.7 5.2.7-3.8 3.6.9 5.1-4.6-2.5-4.6 2.5.9-5.1L4.5 9.9l5.2-.7z" />}
      {kind === 'lock' && (
        <>
          <rect x="4.8" y="10.4" width="14.4" height="9.4" rx="2.6" />
          <path d="M8.4 10.4V7.8a3.6 3.6 0 0 1 7.2 0v2.6" />
        </>
      )}
      {kind === 'bell' && <path d="M12 4a5 5 0 0 0-5 5v3.5L5 15h14l-2-2.5V9a5 5 0 0 0-5-5zM10 18a2 2 0 0 0 4 0" />}
      {kind === 'people' && <path d="M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM16 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM3 20c.7-3 2.8-5 5-5s4.3 2 5 5M11 20c.7-3 2.8-5 5-5s4.3 2 5 5" />}
    </svg>
  );
}

function List({ title, items, onSelect }: { title: string; items: MyProfileListItem[]; onSelect: (item: MyProfileListItem) => void }) {
  return (
    <section className={styles.listZone}>
      <h2>{title}</h2>
      <div className={styles.list}>
        {items.map((item) => (
          <button type="button" onClick={() => onSelect(item)} key={item.key}>
            <span className={styles.icon}><Glyph kind={item.icon} /></span>
            <b>{item.name}</b>
            {item.value === 'toggle' ? <i className={styles.toggle}><em /></i> : (<><span>{item.value}</span><small>›</small></>)}
          </button>
        ))}
      </div>
    </section>
  );
}

export function MyProfileScreen({ model, onEditProfile, onSelectItem, onOpenAllSettings, onLogout }: MyProfileProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1f">
      <section className={styles.content}>
        <header>
          <h1>나</h1>
          <div>
            <button type="button" onClick={onOpenAllSettings} aria-label="전체 설정">☼</button>
          </div>
        </header>
        <section className={styles.profile}>
          <div className={styles.profileTop}>
            <div className={styles.avatar}>{model.avatarInitial}<i /></div>
            <div className={styles.identity}>
              <div><strong>{model.playerName}</strong><b>{model.levelLabel}</b></div>
              <span>{model.familyMeta}</span>
            </div>
            <button type="button" onClick={onEditProfile}>프로필 수정</button>
          </div>
          <div className={styles.stats}>
            {model.stats.map((s) => (
              <div key={s.name}><span>{s.name}</span><strong>{s.value}</strong></div>
            ))}
          </div>
        </section>
        <section className={styles.level}>
          <div><strong>다음 레벨까지</strong><span>{model.levelProgressLabel}</span></div>
          <i><b style={{ width: `${model.levelProgressPercent}%` }} /></i>
          <p>{model.levelHint}</p>
        </section>
        <List title="내 활동" items={model.activity} onSelect={(item) => onSelectItem?.(item)} />
        <List title="설정" items={model.settings} onSelect={(item) => onSelectItem?.(item)} />
        <button type="button" onClick={onLogout} className={styles.logout}>⇥ 로그아웃</button>
      </section>
    </main>
  );
}
