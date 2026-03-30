import { useState, useEffect } from 'react';
import styles from '../AdminDashboard.module.css';
import { adminApi, DeductionItem } from '../api/adminApi';
import { dashboardApi } from '../../UserDashboard/api/dashboardApi';

interface Props {
  playerId: number | null;
  selectedDate: string;
}

export default function PointManager({ playerId, selectedDate }: Props) {
  const [balance, setBalance] = useState(0);
  const [deductions, setDeductions] = useState<DeductionItem[]>([]);
  const [reason, setReason] = useState('');
  const [amount, setAmount] = useState(10);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const abortController = new AbortController();
    if (!playerId) return;
    dashboardApi.fetchDayData(playerId, selectedDate, abortController.signal)
      .then((res) => {
        if (!abortController.signal.aborted) {
          setBalance(res.dailyPoint?.balance ?? 0);
          setDeductions(res.deductions as unknown as DeductionItem[]);
        }
      })
      .catch(() => {});
    return () => abortController.abort();
  }, [playerId, selectedDate]);

  const handleDeduct = async () => {
    if (!playerId || !reason.trim() || amount <= 0) return;
    setLoading(true);
    try {
      await adminApi.createDeduction({ player_id: playerId, date: selectedDate, reason: reason.trim(), amount });
      await adminApi.adjustDailyPoint({ player_id: playerId, date: selectedDate, earned_delta: 0, spent_delta: amount });
      setReason('');
      setAmount(10);
      const res = await dashboardApi.fetchDayData(playerId, selectedDate);
      setBalance(res.dailyPoint?.balance ?? 0);
      setDeductions(res.deductions as unknown as DeductionItem[]);
    } catch {
      alert('차감 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.adminCard}>
      <div className={styles.adminCardTitle}>포인트 관리</div>

      <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>
        현재 보유 포인트: <span style={{ color: '#f59e0b' }}>{balance}P</span>
      </div>

      <div className={styles.adminCardTitle} style={{ fontSize: 14 }}>포인트 차감</div>
      <div className={styles.formGroup}>
        <label className={styles.formLabel}>금액 (P)</label>
        <input
          className={styles.formInput}
          type="number"
          value={amount}
          onChange={(e) => setAmount(Number(e.target.value))}
          min={1}
        />
      </div>
      <div className={styles.formGroup}>
        <label className={styles.formLabel}>사유</label>
        <input
          className={styles.formInput}
          placeholder="간식, 장난감..."
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
      </div>
      <button className={styles.btnDanger} onClick={handleDeduct} disabled={loading}>
        {loading ? '처리 중...' : '차감하기'}
      </button>

      {deductions.length > 0 && (
        <>
          <div className={styles.adminCardTitle} style={{ fontSize: 14, marginTop: 20 }}>차감 이력</div>
          {deductions.map((d) => (
            <div key={d.id} className={styles.listRow}>
              <div className={styles.listRowHeader}>
                <span className={styles.listRowTitle}>{d.reason}</span>
                <span style={{ color: '#e53e3e', fontWeight: 700 }}>-{d.amount}P</span>
              </div>
              <span className={styles.listRowMeta}>{d.date}</span>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
