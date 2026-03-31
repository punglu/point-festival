import { useState, useEffect } from 'react';
import styles from '../AdminDashboard.module.css';
import { adminApi } from '../api/adminApi';
import { httpClient } from '../../../shared/api/httpClient';

interface Props {
  selectedDate: string;
}

interface SenderConfig {
  key: string;
  label: string;
  color: string;
  emoji: string;
}

const SENDERS_FALLBACK: SenderConfig[] = [
  { key: 'dad', label: '아빠', color: 'var(--blue)', emoji: '👨' },
  { key: 'mom', label: '엄마', color: '#db2777', emoji: '👩' },
];

export default function CheerEditor({ selectedDate }: Props) {
  const [senders, setSenders] = useState<SenderConfig[]>([]);
  const [messages, setMessages] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    httpClient.get<{ key: string; value: string }>('/api/configs/cheer.senders')
      .then(res => {
        if (res.data?.value) setSenders(JSON.parse(res.data.value));
        else setSenders(SENDERS_FALLBACK);
      })
      .catch(() => setSenders(SENDERS_FALLBACK));
  }, []);

  useEffect(() => {
    const initial: Record<string, string> = {};
    senders.forEach(s => { initial[s.key] = ''; });
    setMessages(initial);
  }, [senders]);

  useEffect(() => {
    if (!senders.length) return;
    const abortController = new AbortController();
    httpClient.get<{ sender: string; message: string }[]>('/api/cheers', { params: { date: selectedDate }, signal: abortController.signal })
      .then(res => {
        if (!abortController.signal.aborted) {
          const map: Record<string, string> = {};
          senders.forEach(s => { map[s.key] = ''; });
          res.data.forEach((c) => {
            map[c.sender] = c.message;
          });
          setMessages(map);
        }
      })
      .catch(() => {});
    return () => abortController.abort();
  }, [selectedDate, senders]);

  const handleSave = async () => {
    setLoading(true);
    try {
      for (const { key } of senders) {
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

      <div className={styles.cheerDateLabel}>날짜: {selectedDate}</div>

      {senders.map(({ key, label }) => (
        <div key={key} className={styles.cheerRow}>
          <div className={styles.cheerSender}>{label} 메시지</div>
          <textarea
            className={styles.formTextarea}
            placeholder={`${label} 메시지를 입력하세요`}
            value={messages[key] ?? ''}
            onChange={(e) => setMessages((prev) => ({ ...prev, [key]: e.target.value }))}
          />
        </div>
      ))}

      <button className={`${styles.btnPrimary} ${styles.cheerSaveBtn}`} onClick={handleSave} disabled={loading}>
        {loading ? '저장 중...' : '저장'}
      </button>
    </div>
  );
}
