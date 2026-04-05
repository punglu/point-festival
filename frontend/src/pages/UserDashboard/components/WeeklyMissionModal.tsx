import { useState, useEffect } from 'react';
import { httpClient } from '../../../shared/api/httpClient';
import styles from './WeeklyMissionModal.module.css';
import AppIcon from '../../../shared/components/AppIcon';

interface WeeklyMission {
  id: number;
  date: string;
  text: string;
  point: number;
  status: string;
}

interface WeeklyData {
  start_date: string;
  end_date: string;
  total_count: number;
  remaining_count: number;
  remaining_points: number;
  missions: WeeklyMission[];
}

interface Props {
  playerId: number;
  isOpen: boolean;
  onClose: () => void;
  onSelectDate: (date: string) => void;
}

export default function WeeklyMissionModal({ playerId, isOpen, onClose, onSelectDate }: Props) {
  const [data, setData] = useState<WeeklyData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    const controller = new AbortController();
    setLoading(true);

    httpClient
      .get(`/api/missions/weekly-remaining`, {
        params: { player_id: playerId },
        signal: controller.signal,
      })
      .then(res => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [isOpen, playerId]);

  if (!isOpen) return null;

  // 날짜별 그룹핑
  const groupByDate = (missions: WeeklyMission[]) => {
    const map = new Map<string, WeeklyMission[]>();
    for (const m of missions) {
      const arr = map.get(m.date) || [];
      arr.push(m);
      map.set(m.date, arr);
    }
    return map;
  };

  const dayLabel = (dateStr: string) => {
    const d = new Date(dateStr + 'T00:00:00');
    const days = ['일', '월', '화', '수', '목', '금', '토'];
    return `${dateStr.slice(5)} (${days[d.getDay()]})`;
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.header}>
          <h3>
            <AppIcon name="flag" size={18} /> 이번 주 남은 미션
          </h3>
          <button onClick={onClose} className={styles.closeBtn}>✕</button>
        </div>

        {loading ? (
          <p className={styles.loading}>로딩 중...</p>
        ) : !data || data.total_count === 0 ? (
          <div className={styles.emptyState}>
            <AppIcon name="flag" size={48} />
            <p>이번 주 등록된 미션이 없어요.</p>
            <span className={styles.emptyHint}>관리자에게 미션을 요청해보세요!</span>
          </div>
        ) : data.remaining_count === 0 ? (
          <div className={styles.emptyState}>
            <AppIcon name="trophy" size={48} />
            <p>이번 주 미션을 모두 완료했어요!</p>
            <span className={styles.emptyHint}>대단해요! 🎉</span>
          </div>
        ) : (
          <>
            <div className={styles.summary}>
              <div className={styles.summaryItem}>
                <span className={styles.summaryCount}>{data.remaining_count}</span>
                <span className={styles.summaryLabel}>남은 미션</span>
              </div>
              <div className={styles.summaryItem}>
                <span className={styles.summaryPoints}>{data.remaining_points}P</span>
                <span className={styles.summaryLabel}>획득 가능</span>
              </div>
            </div>

            <div className={styles.list}>
              {[...groupByDate(data.missions)].map(([dateStr, missions]) => (
                <div key={dateStr} className={styles.dateGroup}>
                  <div className={styles.dateLabel}>{dayLabel(dateStr)}</div>
                  {missions.map(m => (
                    <div
                      key={m.id}
                      className={styles.missionItem}
                      style={{ cursor: 'pointer' }}
                      onClick={() => { onSelectDate(m.date); onClose(); }}
                    >
                      <span className={styles.missionText}>{m.text}</span>
                      <span className={styles.missionPoint}>{m.point}P</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
