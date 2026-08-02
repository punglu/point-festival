import styles from './ChildInviteScreen.module.css';
import type { ChildInviteProps } from './types';

export function ChildInviteScreen({ model, onApprove, onDismiss }: ChildInviteProps) {
  return (
    <main className={styles.page} data-canonical-screen-id="2f">
      <section>
        <div className={styles.icon}>✉</div>
        <h1>{model.headline}</h1>
        <p>
          {model.description.split('\n').map((line, i) => (
            <span key={i}>
              {line}
              {i < model.description.split('\n').length - 1 && <br />}
            </span>
          ))}
        </p>
        <article>
          <i>{model.letter}</i>
          <div>
            <b>{model.childName}</b>
            <span>{model.detail}</span>
          </div>
        </article>
        <button type="button" onClick={onApprove}>초대 승인하기</button>
        <button type="button" className={styles.secondary} onClick={onDismiss}>나중에 하기</button>
      </section>
    </main>
  );
}
