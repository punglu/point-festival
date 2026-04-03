import { useState } from 'react';
import styles from './AddDeductionModal.module.css';
import AdminModal from '../../../components/AdminModal/AdminModal';
import { POINT_QUICK_VALUES } from '../../../constants/admin.constants';
import type { Player, DailyPoint } from '../../../types/admin.types';

interface Props {
  open:        boolean;
  onClose:     () => void;
  players:     Player[];
  dailyPoints: DailyPoint[];
  defaultDate: string;
  onAdd:       (data: { player_id: number; date: string; reason: string; amount: number }) => Promise<void>;
}

export default function AddDeductionModal({ open, onClose, players, dailyPoints, defaultDate, onAdd }: Props) {
  const [selectedPlayers, setSelectedPlayers] = useState<number[]>([]);
  const [allSelected,     setAllSelected]     = useState(false);
  const [reason,          setReason]          = useState('');
  const [amount,          setAmount]          = useState(10);
  const [date,            setDate]            = useState(defaultDate);
  const [submitting,      setSubmitting]      = useState(false);

  const togglePlayer = (id: number) => {
    setAllSelected(false);
    setSelectedPlayers((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const toggleAll = () => {
    if (allSelected) {
      setAllSelected(false);
      setSelectedPlayers([]);
    } else {
      setAllSelected(true);
      setSelectedPlayers(players.map((p) => p.id));
    }
  };

  const isValid = reason.trim() && amount > 0 && (allSelected || selectedPlayers.length > 0);

  const handleSubmit = async () => {
    if (!isValid) return;
    setSubmitting(true);
    try {
      const targets = allSelected ? players.map((p) => p.id) : selectedPlayers;
      await Promise.all(
        targets.map((player_id) => onAdd({ player_id, date, reason: reason.trim(), amount }))
      );
      setReason(''); setAmount(10); setSelectedPlayers([]); setAllSelected(false);
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  const singleBalance = selectedPlayers.length === 1 && !allSelected
    ? (dailyPoints.find((d) => d.player_id === selectedPlayers[0])?.balance ?? null)
    : null;

  return (
    <AdminModal open={open} onClose={onClose} title="차감 추가" width={420}>
      <div className={styles.formGroup}>
        <div className={styles.label}>대상 플레이어</div>
        <div className={styles.playerCards}>
          <button
            className={allSelected ? styles.playerCardActive : styles.playerCard}
            onClick={toggleAll}
          >
            모두
          </button>
          {players.map((p) => (
            <button
              key={p.id}
              className={selectedPlayers.includes(p.id) && !allSelected ? styles.playerCardActive : styles.playerCard}
              onClick={() => togglePlayer(p.id)}
            >
              {p.name}
            </button>
          ))}
        </div>
        {singleBalance !== null && (
          <div className={styles.balanceNote}>현재 잔액: {singleBalance}pt</div>
        )}
        {allSelected && (
          <div className={styles.balanceNote}>전체 플레이어 {players.length}명에게 적용</div>
        )}
      </div>

      <div className={styles.formGroup}>
        <div className={styles.label}>차감 사유</div>
        <input
          className={styles.input}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="차감 사유를 입력하세요"
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

      <div className={styles.formGroup}>
        <div className={styles.label}>날짜</div>
        <input type="date" className={styles.input} value={date} onChange={(e) => setDate(e.target.value)} />
      </div>

      <button
        className={styles.btnSubmit}
        onClick={handleSubmit}
        disabled={submitting || !isValid}
      >
        {submitting ? '처리 중...' : '차감 적용'}
      </button>
    </AdminModal>
  );
}
