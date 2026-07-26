import { useState, useEffect } from 'react';
import { adminApi } from '../../../api/adminApi';
import { getYesterday } from '../../../../../shared/utils/dateUtils';
import styles from './ImportMissionModal.module.css';
import type { Mission, Player } from '../../../types/admin.types';

interface Props {
  isOpen:     boolean;
  onClose:    () => void;
  onSuccess:  () => void;
  players:    Player[];
  targetDate: string;
}

export default function ImportMissionModal({ isOpen, onClose, onSuccess, players, targetDate }: Props) {
  const [sourceDate,       setSourceDate]       = useState('');
  const [selectedPlayerId, setSelectedPlayerId] = useState<number>(players[0]?.id ?? 0);
  const [missions,         setMissions]         = useState<Mission[]>([]);
  const [checkedIds,       setCheckedIds]       = useState<Set<number>>(new Set());
  const [pointOverrides,   setPointOverrides]   = useState<Record<number, number>>({});
  const [loading,          setLoading]          = useState(false);

  // 어제 날짜를 기본값으로
  useEffect(() => {
    if (!isOpen) return;
    setSourceDate(getYesterday());
    setCheckedIds(new Set());
    setPointOverrides({});
    setMissions([]);
    if (players.length > 0) setSelectedPlayerId(players[0].id);
  }, [isOpen, players]);

  // 원본 날짜 + 플레이어 변경 시 미션 조회
  useEffect(() => {
    if (!isOpen || !sourceDate || !selectedPlayerId) return;
    const ctrl = new AbortController();
    adminApi.getMissions({ player_id: selectedPlayerId, date: sourceDate }, ctrl.signal)
      .then(res => {
        const data = res.data ?? [];
        setMissions(data);
        setCheckedIds(new Set(data.map((m: Mission) => m.id)));
      })
      .catch(() => setMissions([]));
    return () => ctrl.abort();
  }, [isOpen, sourceDate, selectedPlayerId]);

  const toggleCheck = (id: number) => {
    setCheckedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const setPoint = (id: number, point: number) => {
    setPointOverrides(prev => ({ ...prev, [id]: point }));
  };

  const handleImport = async () => {
    if (checkedIds.size === 0) return;
    setLoading(true);
    try {
      const overrides = Object.keys(pointOverrides).length > 0 ? pointOverrides : undefined;
      await adminApi.batchCopyMissions({
        player_id:       selectedPlayerId,
        source_date:     sourceDate,
        target_date:     targetDate,
        mission_ids:     Array.from(checkedIds),
        point_overrides: overrides,
      });
      onSuccess();
      onClose();
    } catch (err) {
      console.error('미션 가져오기 실패:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <h3 className={styles.title}>과거 미션 가져오기</h3>
        <p className={styles.subtitle}>
          선택한 날짜의 미션을 <strong>{targetDate}</strong>로 복사합니다
        </p>

        {/* 플레이어 선택 */}
        <div className={styles.field}>
          <label className={styles.label}>플레이어</label>
          <select
            className={styles.select}
            value={selectedPlayerId}
            onChange={(e) => setSelectedPlayerId(Number(e.target.value))}
          >
            {players.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        {/* 원본 날짜 */}
        <div className={styles.field}>
          <label className={styles.label}>가져올 날짜</label>
          <input
            type="date"
            className={styles.select}
            value={sourceDate}
            onChange={(e) => setSourceDate(e.target.value)}
          />
        </div>

        {/* 미션 목록 (체크박스) */}
        <div className={styles.missionList}>
          {missions.length === 0 ? (
            <p className={styles.empty}>해당 날짜에 미션이 없습니다</p>
          ) : (
            missions.map(m => (
              <div key={m.id} className={styles.missionItem}>
                <input
                  type="checkbox"
                  checked={checkedIds.has(m.id)}
                  onChange={() => toggleCheck(m.id)}
                />
                <span className={styles.missionText}>{m.text}</span>
                <input
                  type="number"
                  className={styles.pointInput}
                  value={pointOverrides[m.id] ?? m.point}
                  min={1}
                  onChange={(e) => setPoint(m.id, Number(e.target.value))}
                />
                <span className={styles.pointUnit}>P</span>
              </div>
            ))
          )}
        </div>

        <div className={styles.actions}>
          <button className={styles.cancelBtn} onClick={onClose}>취소</button>
          <button
            className={styles.submitBtn}
            onClick={handleImport}
            disabled={loading || checkedIds.size === 0}
          >
            {loading ? '가져오는 중...' : `${checkedIds.size}건 가져오기`}
          </button>
        </div>
      </div>
    </div>
  );
}
