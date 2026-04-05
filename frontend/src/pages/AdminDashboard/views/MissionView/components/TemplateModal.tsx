import { useState, useEffect } from 'react';
import { httpClient } from '../../../../../shared/api/httpClient';
import styles from './TemplateModal.module.css';

interface Template {
  id: number;
  player_id: number;
  text: string;
  point: number;
  day_of_week: number;
  is_active: boolean;
  group_id?: string | null;
}

interface Player {
  id: number;
  name: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  players: Player[];
  editingTemplate?: Template | null;
}

const DAY_LABELS = ['월', '화', '수', '목', '금', '토', '일'];
const DAY_BITS   = [1, 2, 4, 8, 16, 32, 64];

export default function TemplateModal({ isOpen, onClose, onSuccess, players, editingTemplate }: Props) {
  const [text,         setText]         = useState('');
  const [point,        setPoint]        = useState(5);
  const [selectedDays, setSelectedDays] = useState<number[]>([0, 1, 2, 3, 4, 5, 6]); // 매일 기본
  const [targetPlayers, setTargetPlayers] = useState<number[]>([]);             // 빈 배열 = 전체
  const [loading,      setLoading]      = useState(false);

  const isEditMode = !!editingTemplate;

  useEffect(() => {
    if (!isOpen) return;
    if (editingTemplate) {
      setText(editingTemplate.text);
      setPoint(editingTemplate.point);
      const days: number[] = [];
      DAY_BITS.forEach((bit, i) => { if (editingTemplate.day_of_week & bit) days.push(i); });
      setSelectedDays(days);
      setTargetPlayers([editingTemplate.player_id]);
    } else {
      setText('');
      setPoint(5);
      setSelectedDays([0, 1, 2, 3, 4, 5, 6]);
      setTargetPlayers([]);
    }
  }, [editingTemplate, isOpen]);

  const toggleDay = (i: number) =>
    setSelectedDays(prev => prev.includes(i) ? prev.filter(d => d !== i) : [...prev, i]);

  const togglePlayer = (id: number) =>
    setTargetPlayers(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]);

  const handleSubmit = async () => {
    if (!text.trim() || selectedDays.length === 0) return;
    const dayOfWeek = selectedDays.reduce((acc, i) => acc | DAY_BITS[i], 0);
    setLoading(true);
    try {
      if (isEditMode && editingTemplate) {
        await httpClient.patch(`/api/mission-templates/${editingTemplate.id}`, {
          text: text.trim(), point, day_of_week: dayOfWeek,
        });
      } else {
        const targets  = targetPlayers.length > 0 ? targetPlayers : players.map(p => p.id);
        const groupId  = targets.length > 1 ? crypto.randomUUID() : undefined;
        for (const pid of targets) {
          await httpClient.post('/api/mission-templates', {
            player_id: pid, text: text.trim(), point, day_of_week: dayOfWeek,
            ...(groupId ? { group_id: groupId } : {}),
          });
        }
        // 생성 직후 오늘 날짜 Lazy Init
        await httpClient.post('/api/mission-templates/generate');
      }
      onSuccess();
      onClose();
    } catch (err) {
      console.error('템플릿 저장 실패:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <h3 className={styles.title}>
          {isEditMode ? '반복 미션 편집' : '반복 미션 추가'}
        </h3>

        {/* 대상 플레이어 (신규 모드에서만) */}
        {!isEditMode && (
          <div className={styles.field}>
            <label className={styles.label}>대상 플레이어</label>
            <div className={styles.chipGroup}>
              <button
                className={`${styles.chip} ${targetPlayers.length === 0 ? styles.chipActive : ''}`}
                onClick={() => setTargetPlayers([])}
              >
                전체
              </button>
              {players.map(p => (
                <button
                  key={p.id}
                  className={`${styles.chip} ${targetPlayers.includes(p.id) ? styles.chipActive : ''}`}
                  onClick={() => togglePlayer(p.id)}
                >
                  {p.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 반복 요일 */}
        <div className={styles.field}>
          <label className={styles.label}>반복 요일</label>
          <div className={styles.chipGroup}>
            {DAY_LABELS.map((label, i) => (
              <button
                key={i}
                className={`${styles.dayChip} ${selectedDays.includes(i) ? styles.dayChipActive : ''}`}
                onClick={() => toggleDay(i)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* 미션명 */}
        <div className={styles.field}>
          <label className={styles.label}>미션명</label>
          <input
            className={styles.input}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="예: 양치하기"
          />
        </div>

        {/* 포인트 */}
        <div className={styles.field}>
          <label className={styles.label}>포인트</label>
          <input
            className={styles.input}
            type="number"
            min={1}
            max={100}
            value={point}
            onChange={(e) => setPoint(Number(e.target.value))}
          />
        </div>

        <div className={styles.actions}>
          <button className={styles.cancelBtn} onClick={onClose}>취소</button>
          <button
            className={styles.submitBtn}
            onClick={handleSubmit}
            disabled={loading || !text.trim() || selectedDays.length === 0}
          >
            {loading ? '저장 중...' : isEditMode ? '수정' : '추가'}
          </button>
        </div>
      </div>
    </div>
  );
}
