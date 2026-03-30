import { useState } from 'react';
import styles from '../UserDashboard.module.css';
import { MissionResponse } from '../api/dashboardApi';

interface Props {
  myProposals: MissionResponse[];
  proposeMission: (text: string, point: number, reason?: string) => Promise<void>;
}

const PROPOSAL_STATUS: Record<string, string> = {
  proposed: '검토 중',
  active: '승인됨',
  rejected: '거절됨',
};

export default function MissionProposal({ myProposals, proposeMission }: Props) {
  const [text, setText] = useState('');
  const [point, setPoint] = useState('');
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    const p = parseInt(point, 10);
    if (!text.trim() || isNaN(p) || p <= 0) return;
    setSubmitting(true);
    try {
      await proposeMission(text.trim(), p, reason.trim() || undefined);
      setText('');
      setPoint('');
      setReason('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.proposalSection}>
      <div className={styles.proposalTitle}>✏️ 미션 제안</div>

      <input
        className={styles.proposalInput}
        placeholder="미션 내용을 입력하세요"
        value={text}
        onChange={e => setText(e.target.value)}
        maxLength={200}
      />
      <div className={styles.proposalRow}>
        <input
          className={styles.proposalInput}
          placeholder="포인트"
          type="number"
          min={1}
          value={point}
          onChange={e => setPoint(e.target.value)}
          style={{ width: 100, flex: 'none' }}
        />
        <input
          className={styles.proposalInput}
          placeholder="제안 이유 (선택)"
          value={reason}
          onChange={e => setReason(e.target.value)}
          style={{ flex: 1 }}
        />
      </div>
      <button
        className={styles.proposalBtn}
        onClick={handleSubmit}
        disabled={submitting}
      >
        {submitting ? '제출 중...' : '제안하기'}
      </button>

      {myProposals.length > 0 && (
        <>
          <div className={styles.sectionHeader}>내 제안 현황</div>
          <div className={styles.proposalList}>
            {myProposals.map(m => (
              <div key={m.id} className={styles.proposalItem}>
                <span>{m.text}</span>
                <span style={{ color: m.status === 'rejected' ? '#f87171' : m.status === 'active' ? '#34d399' : '#fbbf24', fontSize: 12, fontWeight: 600 }}>
                  {PROPOSAL_STATUS[m.status] ?? m.status}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
