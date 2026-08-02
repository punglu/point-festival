import styles from './FamilyMembersScreen.module.css';
import type { FamilyMembersProps } from './types';

const TONES = [styles.tone0, styles.tone1, styles.tone2, styles.tone3];

export function FamilyMembersScreen({ model, onBack, onEdit, onSelectMember, onInvite, onViewRequests }: FamilyMembersProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="1q">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <div><h1>가족 구성원</h1><span>{model.memberSummary}</span></div>
        <button type="button" onClick={onEdit}>편집</button>
      </header>
      <section className={styles.content}>
        <section className={styles.family}>
          <span>{model.familyName}</span>
          <b>{model.familyTagline}</b>
          <p>{model.familyDescription}</p>
        </section>
        <section className={styles.list}>
          {model.members.map((m, index) => (
            <article key={m.name}>
              <i className={TONES[index % TONES.length]}>{m.letter}</i>
              <div><b>{m.name}</b><span>{m.role}</span></div>
              {m.isGuardian && <em>보호자</em>}
              <button type="button" onClick={() => onSelectMember?.(m)}>›</button>
            </article>
          ))}
        </section>
        <button type="button" onClick={onInvite} className={styles.invite}>＋ 가족 구성원 초대</button>
        {model.pendingChildRequestName && (
          <button type="button" onClick={onViewRequests} className={styles.requestNotice}>
            {model.pendingChildRequestName}님의 가족 참여 요청이 도착했어요 →
          </button>
        )}
        <aside>
          ♧
          <div><b>가족 구성원은 최대 8명까지 초대할 수 있어요.</b><span>초대받은 구성원은 PIN 설정 후 참여할 수 있습니다.</span></div>
        </aside>
      </section>
    </main>
  );
}
