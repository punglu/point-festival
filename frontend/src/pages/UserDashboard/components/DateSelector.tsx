import styles from '../UserDashboard.module.css';

interface Props {
  selectedDate: string;
  quickDate: (offset: number) => void;
  setSelectedDate: (date: string) => void;
}

export default function DateSelector({ selectedDate, quickDate, setSelectedDate }: Props) {
  const today = new Date().toISOString().slice(0, 10);
  const yesterday = (() => { const d = new Date(); d.setDate(d.getDate() - 1); return d.toISOString().slice(0, 10); })();
  const tomorrow = (() => { const d = new Date(); d.setDate(d.getDate() + 1); return d.toISOString().slice(0, 10); })();

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
