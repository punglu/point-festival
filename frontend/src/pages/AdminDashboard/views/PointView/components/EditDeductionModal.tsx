import { useState } from 'react';
import styles from './EditDeductionModal.module.css';
import AdminModal from '../../../components/AdminModal/AdminModal';
import { POINT_QUICK_VALUES } from '../../../constants/admin.constants';
import type { Deduction } from '../../../types/admin.types';

interface Props {
  open:       boolean;
  onClose:    () => void;
  deduction:  Deduction;
  onSave:     (data: { reason: string; amount: number }) => Promise<void>;
}

export default function EditDeductionModal({ open, onClose, deduction, onSave }: Props) {
  const [reason,     setReason]     = useState(deduction.reason);
  const [amount,     setAmount]     = useState(deduction.amount);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!reason.trim() || amount <= 0) return;
    setSubmitting(true);
    try {
      await onSave({ reason: reason.trim(), amount });
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AdminModal open={open} onClose={onClose} title="차감 수정" width={400}>
      <div className={styles.formGroup}>
        <div className={styles.label}>차감 사유</div>
        <input
          className={styles.input}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="차감 사유"
        />
      </div>

      <div className={styles.formGroup}>
        <div className={styles.label}>차감 포인트</div>
        <div className={styles.pointRow}>
          <input
            type="number"
            className={styles.pointInput}
            value={amount}
            min={1}
            onChange={(e) => setAmount(Number(e.target.value))}
          />
          <div className={styles.quickBtns}>
            {POINT_QUICK_VALUES.map((v) => (
              <button key={v} className={styles.quickBtn} onClick={() => setAmount(v)}>{v}pt</button>
            ))}
          </div>
        </div>
      </div>

      <button
        className={styles.btnSubmit}
        onClick={handleSubmit}
        disabled={submitting || !reason.trim()}
      >
        {submitting ? '저장 중...' : '저장'}
      </button>
    </AdminModal>
  );
}
