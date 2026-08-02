import { useState } from 'react';
import styles from './FamilyInviteCancelScreen.module.css';
import type { FamilyInviteCancelProps } from './types';
export function FamilyInviteCancelScreen({ model, onBack, onConfirm }: FamilyInviteCancelProps) {
  const [reason, setReason] = useState('');
  return (
    <main className={styles.screen} data-canonical-screen-id="3i" data-canonical-screen-label="가족 초대 취소" data-canonical-source="wave7-full-authority">
      <header>
        <h1>{model.title}</h1>
        <button type="button" onClick={onBack}>✕</button>
      </header>
      <div className={styles.code}>
        <div>
          <strong>{model.code}</strong>
          <span>{model.invitee} · {model.issuedAt}</span>
        </div>
        <em>{model.status}</em>
      </div>
      <p className={styles.warning}>{model.warning}</p>
      <label className={styles.label}>{model.reasonLabel}</label>
      <textarea className={styles.reason} placeholder={model.reasonPlaceholder} value={reason} onChange={(e) => setReason(e.target.value)} />
      <div className={styles.actions}>
        <button type="button" className={styles.back} onClick={onBack}>돌아가기</button>
        <button type="button" className={styles.confirm} onClick={() => onConfirm?.(reason)}>초대 취소하기</button>
      </div>
    </main>
  );
}
