import { useState } from 'react';
import styles from './NewMissionModal.module.css';
import { getLocalToday, shiftDay } from '../../../../../shared/utils/dateUtils';
import AdminModal from '../../../components/AdminModal/AdminModal';
import { POINT_QUICK_VALUES } from '../../../constants/admin.constants';
import type { Player } from '../../../types/admin.types';

interface Props {
  open:        boolean;
  onClose:     () => void;
  players:     Player[];
  defaultDate: string;
  onCreate:    (data: { player_id: number; date: string; text: string; point: number; group_id?: string }) => Promise<void>;
}

type DateMode = 'today' | 'tomorrow' | 'custom';

export default function NewMissionModal({ open, onClose, players, defaultDate, onCreate }: Props) {
  const today    = getLocalToday();
  const tomorrow = shiftDay(today, 1);

  const [selectedPlayerIds, setSelectedPlayerIds] = useState<number[]>([]);
  const [text,      setText]      = useState('');
  const [point,     setPoint]     = useState(10);
  const [dateMode,  setDateMode]  = useState<DateMode>('today');
  const [customDate, setCustomDate] = useState(defaultDate);
  const [submitting, setSubmitting] = useState(false);

  const getDate = () => dateMode === 'today' ? today : dateMode === 'tomorrow' ? tomorrow : customDate;

  const togglePlayer = (id: number) => {
    setSelectedPlayerIds((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    if (selectedPlayerIds.length === players.length) {
      setSelectedPlayerIds([]);
    } else {
      setSelectedPlayerIds(players.map((p) => p.id));
    }
  };

  const handleSubmit = async () => {
    if (!text.trim() || selectedPlayerIds.length === 0) return;
    setSubmitting(true);
    try {
      // 2명 이상에게 할당 시 같은 group_id 공유 → 이후 일괄 삭제 가능
      const groupId = selectedPlayerIds.length > 1 ? crypto.randomUUID() : undefined;
      await Promise.all(
        selectedPlayerIds.map((pid) =>
          onCreate({ player_id: pid, date: getDate(), text: text.trim(), point, group_id: groupId })
        )
      );
      setText(''); setPoint(10); setSelectedPlayerIds([]);
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AdminModal open={open} onClose={onClose} title="새 미션 추가" width={440}>
      <div className={styles.formGroup}>
        <div className={styles.label}>대상 플레이어</div>
        <div className={styles.playerCards}>
          <button
            className={selectedPlayerIds.length === players.length ? styles.playerCardActive : styles.playerCard}
            onClick={selectAll}
          >
            모두
          </button>
          {players.map((p) => (
            <button
              key={p.id}
              className={selectedPlayerIds.includes(p.id) ? styles.playerCardActive : styles.playerCard}
              onClick={() => togglePlayer(p.id)}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.formGroup}>
        <div className={styles.label}>미션 이름</div>
        <input
          className={styles.input}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="미션 내용을 입력하세요"
        />
      </div>

      <div className={styles.formGroup}>
        <div className={styles.label}>포인트</div>
        <div className={styles.pointRow}>
          <input
            type="number"
            className={styles.pointInput}
            value={point}
            min={1}
            onChange={(e) => setPoint(Number(e.target.value))}
          />
          <div className={styles.quickBtns}>
            {POINT_QUICK_VALUES.map((v) => (
              <button key={v} className={styles.quickBtn} onClick={() => setPoint(v)}>{v}pt</button>
            ))}
          </div>
        </div>
      </div>

      <div className={styles.formGroup}>
        <div className={styles.label}>날짜</div>
        <div className={styles.dateGroup}>
          <button className={dateMode === 'today'    ? styles.dateBtnActive : styles.dateBtn} onClick={() => setDateMode('today')}>오늘</button>
          <button className={dateMode === 'tomorrow' ? styles.dateBtnActive : styles.dateBtn} onClick={() => setDateMode('tomorrow')}>내일</button>
          <button className={dateMode === 'custom'   ? styles.dateBtnActive : styles.dateBtn} onClick={() => setDateMode('custom')}>날짜 선택</button>
          {dateMode === 'custom' && (
            <input type="date" className={styles.input} value={customDate} onChange={(e) => setCustomDate(e.target.value)} />
          )}
        </div>
      </div>

      <button className={styles.btnSubmit} onClick={handleSubmit} disabled={submitting || !text.trim() || selectedPlayerIds.length === 0}>
        {submitting ? '추가 중...' : '미션 추가'}
      </button>
    </AdminModal>
  );
}
