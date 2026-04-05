import { useState, useEffect, useCallback } from 'react';
import { httpClient } from '../../../../../shared/api/httpClient';
import styles from './WeeklyGrid.module.css';
import { getLocalToday, getMonday, getWeekDates, getWeekLabel, shiftWeek } from '../../../../../shared/utils/dateUtils';

interface DailySummary {
  total: number;
  done: number;
  points: number;
  pending: number;
}

interface PlayerWeek {
  player_id: number;
  player_name: string;
  player_photo?: string | null;
  daily: Record<string, DailySummary>;
}

interface WeeklyGridProps {
  onSelectCell: (playerId: number, date: string) => void;
  onBulkApprove: (playerId: number, date: string) => void;
}

const DAY_NAMES = ['월', '화', '수', '목', '금', '토', '일'];

export default function WeeklyGrid({ onSelectCell, onBulkApprove }: WeeklyGridProps) {
  const [weekStart, setWeekStart] = useState(() => getMonday());
  const [data, setData] = useState<PlayerWeek[]>([]);
  const [selectedCell, setSelectedCell] = useState<{ playerId: number; date: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const today = getLocalToday();

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const { data: res } = await httpClient.get('/api/admin/weekly-summary', {
        params: { week_start: weekStart },
      });
      setData(res.players);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  }, [weekStart]);

  useEffect(() => { loadData(); }, [loadData]);

  const dates    = getWeekDates(weekStart);
  const weekLabel = getWeekLabel(weekStart);

  const handlePrev     = () => { setWeekStart(shiftWeek(weekStart, -1)); setSelectedCell(null); };
  const handleNext     = () => { setWeekStart(shiftWeek(weekStart,  1)); setSelectedCell(null); };
  const handleThisWeek = () => { setWeekStart(getMonday());              setSelectedCell(null); };

  const handleCellClick = (playerId: number, date: string) => {
    setSelectedCell({ playerId, date });
    onSelectCell(playerId, date);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h3 className={styles.title}>주간 현황</h3>
          <span className={styles.weekRange}>{weekLabel}</span>
        </div>
        <div className={styles.nav}>
          <button className={styles.navBtn} onClick={handlePrev}>{'< 이전 주'}</button>
          <button className={styles.navBtnActive} onClick={handleThisWeek}>이번 주</button>
          <button className={styles.navBtn} onClick={handleNext}>{'다음 주 >'}</button>
        </div>
      </div>

      {loading ? (
        <p className={styles.loading}>로딩 중...</p>
      ) : (
        <div className={styles.gridWrap}>
          <div className={styles.gridHeader}>
            <div className={styles.ghLabel} />
            {dates.map((d, i) => {
              const isWeekend = i >= 5;
              return (
                <div key={d} className={[styles.ghCell, d === today ? styles.ghToday : '', isWeekend ? styles.ghWeekend : ''].filter(Boolean).join(' ')}>
                  <div className={styles.ghDay}>{DAY_NAMES[i]}</div>
                  <div className={styles.ghDate}>{d.slice(5)}</div>
                </div>
              );
            })}
          </div>
          {data.map(player => (
            <div key={player.player_id} className={styles.gridRow}>
              <div className={styles.grName}>
                {player.player_photo ? (
                  <img src={player.player_photo} alt={player.player_name} className={styles.grAvatar} />
                ) : (
                  <div className={styles.grInitial}>{player.player_name[0] ?? '?'}</div>
                )}
                <span>{player.player_name}</span>
              </div>
              {dates.map((d, i) => {
                const s = player.daily[d] || { total: 0, done: 0, points: 0, pending: 0 };
                const isSelected = selectedCell?.playerId === player.player_id && selectedCell?.date === d;
                const isWeekend = i >= 5;
                return (
                  <div
                    key={d}
                    className={[styles.grCell, isSelected ? styles.grSelected : '', d === today ? styles.grCellToday : '', isWeekend ? styles.grCellWeekend : ''].filter(Boolean).join(' ')}
                    onClick={() => handleCellClick(player.player_id, d)}
                  >
                    {s.total > 0 ? (
                      <>
                        <div className={`${styles.grTotal} ${s.done === s.total ? styles.grDone : s.pending > 0 ? styles.grPending : styles.grActive}`}>
                          {s.done}/{s.total}
                        </div>
                        <div className={styles.grDetail}>{s.points}P</div>
                        {s.pending > 0 && (
                          <button
                            className={styles.approveBtn}
                            onClick={(e) => { e.stopPropagation(); onBulkApprove(player.player_id, d); loadData(); }}
                          >
                            전체 승인
                          </button>
                        )}
                      </>
                    ) : (
                      <div className={styles.grEmpty}>-</div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
