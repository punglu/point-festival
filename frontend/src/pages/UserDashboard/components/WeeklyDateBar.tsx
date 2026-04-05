import { useMemo } from 'react';
import styles from './WeeklyDateBar.module.css';
import { getLocalToday, getWeekDates, getWeekLabel, parseDate } from '../../../shared/utils/dateUtils';

interface DayInfo {
  date: string;
  dayNum: number;
  dayName: string;
  isToday: boolean;
  isPast: boolean;
  missionCount: number;
  doneCount: number;
  activeCount: number;
}

interface WeeklyDateBarProps {
  weekStart: string;
  selectedDate: string;
  missionsByDate: Record<string, { status: string }[]>;
  onSelectDate: (date: string) => void;
  onPrevWeek: () => void;
  onNextWeek: () => void;
  onToday: () => void;
}

const DAY_NAMES = ['월', '화', '수', '목', '금', '토', '일'];

export default function WeeklyDateBar({
  weekStart, selectedDate, missionsByDate, onSelectDate, onPrevWeek, onNextWeek, onToday
}: WeeklyDateBarProps) {
  const today = getLocalToday();

  const days: DayInfo[] = useMemo(() => {
    const weekDates = getWeekDates(weekStart);
    return weekDates.map((dateStr, i) => {
      const d = parseDate(dateStr);
      const missions = missionsByDate[dateStr] || [];
      return {
        date: dateStr,
        dayNum: d.getDate(),
        dayName: DAY_NAMES[i],
        isToday: dateStr === today,
        isPast: dateStr < today,
        missionCount: missions.length,
        doneCount: missions.filter(m => m.status === 'completed').length,
        activeCount: missions.filter(m => m.status === 'active').length,
      };
    });
  }, [weekStart, missionsByDate, today]);

  const weekLabel = useMemo(() => getWeekLabel(weekStart), [weekStart]);

  return (
    <>
      <div className={styles.weekNav}>
        <button className={styles.navBtn} onClick={onPrevWeek}>{'< 이전 주'}</button>
        <span className={styles.weekLabel}>
          {weekLabel}
          <button className={styles.todayBtn} onClick={onToday}>오늘</button>
        </span>
        <button className={styles.navBtn} onClick={onNextWeek}>{'다음 주 >'}</button>
      </div>
      <div className={styles.dateBar}>
        {days.map(day => (
          <div
            key={day.date}
            className={`${styles.day} ${day.isToday ? styles.today : ''} ${day.isPast ? styles.past : ''} ${day.date === selectedDate ? styles.selected : ''}`}
            onClick={() => onSelectDate(day.date)}
          >
            <div className={styles.dayName}>{day.dayName}</div>
            <div className={styles.dayNum}>{day.dayNum}</div>
            {day.missionCount > 0 && (
              <div className={styles.dots}>
                {Array.from({ length: Math.min(day.missionCount, 4) }, (_, i) => (
                  <span
                    key={i}
                    className={`${styles.dot} ${i < day.doneCount ? styles.dotDone : i < day.doneCount + day.activeCount ? styles.dotActive : ''}`}
                  />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </>
  );
}
