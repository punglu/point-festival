import { useState } from 'react';
import styles from './AccountDeletionConfirmScreen.module.css';
import type { AccountDeletionConfirmProps } from './types';
export function AccountDeletionConfirmScreen({ model, onBack, onConfirm }: AccountDeletionConfirmProps) {
  const [typed, setTyped] = useState(model.confirmWord);
  return (
    <main className={styles.screen} data-canonical-screen-id="3h" data-canonical-screen-label="계정 탈퇴 확인" data-canonical-source="wave7-full-authority">
      <header>
        <button type="button" onClick={onBack}>←</button>
        <h1>{model.title}</h1>
      </header>
      <i className={styles.warn}>!</i>
      <strong className={styles.question}>{model.question}</strong>
      <div className={styles.card}>
        <span>{model.itemsIntro}</span>
        <ul>
          {model.items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
      <label className={styles.hint}>{model.confirmHint}</label>
      <input className={styles.input} value={typed} onChange={(e) => setTyped(e.target.value)} />
      <div className={styles.actions}>
        <button type="button" className={styles.danger} onClick={() => onConfirm?.(typed)}>계정 탈퇴하기</button>
        <button type="button" className={styles.cancel} onClick={onBack}>취소</button>
      </div>
    </main>
  );
}
