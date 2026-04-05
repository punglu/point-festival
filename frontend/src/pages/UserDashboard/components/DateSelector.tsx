import styles from '../UserDashboard.module.css';
import { getLocalToday, getYesterday, shiftDay } from '../../../shared/utils/dateUtils';

interface Props {
  selectedDate: string;
  quickDate: (offset: number) => void;
  setSelectedDate: (date: string) => void;
}

export default function DateSelector({ selectedDate, quickDate, setSelectedDate }: Props) {
  const today    = getLocalToday();
  const yesterday = getYesterday();
  const tomorrow  = shiftDay(today, 1);

  return (
    <div className={styles.dateBar}>
      <button
        className={`${styles.dateChip} ${selectedDate === yesterday ? styles.dateChipActive : ''}`}
        onClick={() => quickDate(-1)}
      >
        어제
      </button>
      <button
        className={`${styles.dateChip} ${selectedDate === today ? styles.dateChipActive : ''}`}
        onClick={() => quickDate(0)}
      >
        오늘
      </button>
      <button
        className={`${styles.dateChip} ${selectedDate === tomorrow ? styles.dateChipActive : ''}`}
        onClick={() => quickDate(1)}
      >
        내일
      </button>
      <input
        type="date"
        value={selectedDate}
        onChange={e => setSelectedDate(e.target.value)}
        className={styles.dateDisplay}
      />
    </div>
  );
}
