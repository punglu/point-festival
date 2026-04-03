import { useState } from 'react';
import styles from './AddPlayerModal.module.css';
import AdminModal from '../../../components/AdminModal/AdminModal';

interface Props {
  open:    boolean;
  onClose: () => void;
  onAdd:   (data: { name: string; pin: string }) => Promise<void>;
}

export default function AddPlayerModal({ open, onClose, onAdd }: Props) {
  const [name,       setName]       = useState('');
  const [pin,        setPin]        = useState('');
  const [pinConfirm, setPinConfirm] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error,      setError]      = useState('');

  const isValid = name.trim().length > 0 && pin.length >= 4 && pin === pinConfirm;

  const handleSubmit = async () => {
    if (!isValid) return;
    if (!/^\d{4,6}$/.test(pin)) {
      setError('PIN은 4~6자리 숫자여야 합니다');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await onAdd({ name: name.trim(), pin });
      setName(''); setPin(''); setPinConfirm('');
      onClose();
    } catch {
      setError('플레이어 추가 실패. 이름이 중복되었을 수 있습니다.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AdminModal open={open} onClose={onClose} title="플레이어 추가" width={380}>
      <div className={styles.formGroup}>
        <div className={styles.label}>이름</div>
        <input
          className={styles.input}
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="플레이어 이름"
          maxLength={20}
        />
      </div>

      <div className={styles.formGroup}>
        <div className={styles.label}>PIN (4~6자리 숫자)</div>
        <input
          className={styles.input}
          type="password"
          inputMode="numeric"
          value={pin}
          onChange={(e) => setPin(e.target.value)}
          placeholder="••••"
          maxLength={6}
        />
      </div>

      <div className={styles.formGroup}>
        <div className={styles.label}>PIN 확인</div>
        <input
          className={styles.input}
          type="password"
          inputMode="numeric"
          value={pinConfirm}
          onChange={(e) => setPinConfirm(e.target.value)}
          placeholder="••••"
          maxLength={6}
        />
        {pinConfirm && pin !== pinConfirm && (
          <div className={styles.hint}>PIN이 일치하지 않습니다</div>
        )}
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <button
        className={styles.btnSubmit}
        onClick={handleSubmit}
        disabled={submitting || !isValid}
      >
        {submitting ? '추가 중...' : '플레이어 추가'}
      </button>
    </AdminModal>
  );
}
