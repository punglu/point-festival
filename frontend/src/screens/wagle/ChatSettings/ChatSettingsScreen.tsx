import styles from './ChatSettingsScreen.module.css';
import type { ChatSettingsProps } from './types';

export function ChatSettingsScreen({ model, onBack, onOpenItem, onLeave }: ChatSettingsProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1t">
      <header>
        <button type="button" onClick={onBack} aria-label="뒤로">←</button>
        <h1>채팅방 설정</h1>
      </header>
      <section>
        <div className={styles.room}>
          <i>{model.roomName.charAt(0)}</i>
          <b>{model.roomName}</b>
          <span>{model.memberSummary}</span>
        </div>
        <h2>채팅방 정보</h2>
        {model.items.map((item) => (
          <button type="button" key={item.name} onClick={() => onOpenItem?.(item)}>
            <span>
              {item.name}
              <small>{item.description}</small>
            </span>
            {item.hasToggle ? <i className={styles.toggle} /> : <em>›</em>}
          </button>
        ))}
        <h2>참여자</h2>
        {model.members.map((member, index) => (
          <div className={styles.person} key={index}>
            <i>{member.name}</i>
            <span>{member.name}</span>
          </div>
        ))}
        <button type="button" className={styles.leave} onClick={onLeave}>
          채팅방 나가기
        </button>
      </section>
    </main>
  );
}
