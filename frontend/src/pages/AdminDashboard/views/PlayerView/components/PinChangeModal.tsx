import { useState } from 'react';
import styles from './PinChangeModal.module.css';
import AdminModal from '../../../components/AdminModal/AdminModal';
import type { Player } from '../../../types/admin.types';

interface Props {
  open:     boolean;
  onClose:  () => void;
  player:   Player;
  onSave:   (pin: string) => Promise<void>;
}

export default function PinChangeModal({ open, onClose, player, onSave }: Props) {
  const [pin,        setPin]        = useState('');
  const [confirm,    setConfirm]    = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error,      setError]      = useState('');

  const handleSubmit = async () => {
    if (pin.length !== 4 || !/^\d{4}$/.test(pin)) {
      setError('4자리 숫자를 입력하세요'); return;
    }
    if (pin !== confirm) {
      setError('PIN이 일치하지 않습니다'); return;
    }
    setError('');
    setSubmitting(true);
    try {
      await onSave(pin);
      setPin(''); setConfirm('');
      onClose();
    } catch {
      setError('변경 실패. 다시 시도해주세요');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AdminModal open={open} onClose={onClose} title={`${player.name} PIN 변경`} width={360}>
      <div className={styles.formGroup}>
        <div className={styles.label}>새 PIN (4자리)</div>
        <input
          type="password"
          className={styles.input}
          value={pin}
          maxLength={4}
          placeholder="••••"
          onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
        />
        <div className={styles.hint}>숫자 4자리</div>
      </div>

      <div className={styles.formGroup}>
        <div className={styles.label}>PIN 확인</div>
        <input
          type="password"
          className={styles.input}
          value={confirm}
          maxLength={4}
          placeholder="••••"
          onChange={(e) => setConfirm(e.target.value.replace(/\D/g, '').slice(0, 4))}
        />
        {error && <div className={styles.error}>{error}</div>}
      </div>

      <button
        className={styles.btnSubmit}
        onClick={handleSubmit}
        disabled={submitting || pin.length !== 4 || confirm.length !== 4}
      >
        {submitting ? '변경 중...' : 'PIN 변경'}
      </button>
    </AdminModal>
  );
}
