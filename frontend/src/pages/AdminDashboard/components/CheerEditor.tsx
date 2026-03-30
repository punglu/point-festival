import { useState, useEffect } from 'react';
import styles from '../AdminDashboard.module.css';
import { adminApi } from '../api/adminApi';
import { dashboardApi } from '../../UserDashboard/api/dashboardApi';

interface Props {
  selectedDate: string;
}

const SENDERS = [
  { key: 'dad', label: '아빠 메시지' },
  { key: 'mom', label: '엄마 메시지' },
] as const;

export default function CheerEditor({ selectedDate }: Props) {
  const [messages, setMessages] = useState<Record<string, string>>({ dad: '', mom: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const abortController = new AbortController();
    dashboardApi.fetchDayData(1, selectedDate, abortController.signal)
      .then((res) => {
        if (!abortController.signal.aborted) {
          const map: Record<string, string> = { dad: '', mom: '' };
          res.cheers.forEach((c) => { map[c.sender] = c.message; });
          setMessages(map);
        }
      })
      .catch(() => {});
    return () => abortController.abort();
  }, [selectedDate]);

  const handleSave = async () => {
    setLoading(true);
    try {
      for (const { key } of SENDERS) {
        if (messages[key]) {
          await adminApi.upsertCheer(selectedDate, { date: selectedDate, sender: key, message: messages[key] });
        }
      }
      alert('저장 완료');
    } catch {
      alert('저장 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.adminCard}>
      <div className={styles.adminCardTitle}>응원 메시지</div>

      <div style={{ fontSize: 13, color: '#718096', marginBottom: 12 }}>날짜: {selectedDate}</div>

      {SENDERS.map(({ key, label }) => (
        <div key={key} className={styles.cheerRow}>
          <div className={styles.cheerSender}>{label}</div>
          <textarea
            className={styles.formTextarea}
            placeholder={`${label}을 입력하세요`}
            value={messages[key]}
            onChange={(e) => setMessages((prev) => ({ ...prev, [key]: e.target.value }))}
          />
        </div>
      ))}

      <button className={styles.btnPrimary} style={{ width: '100%', marginTop: 12 }} onClick={handleSave} disabled={loading}>
        {loading ? '저장 중...' : '저장'}
      </button>
    </div>
  );
}
