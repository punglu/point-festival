import styles from './DateSelector.module.css';
import { getLocalToday, shiftDay } from '../../../../shared/utils/dateUtils';

interface DateSelectorProps {
  selected: string;
  onSelect: (date: string) => void;
}

function offset(days: number): string {
  const today = getLocalToday();
  if (days === 0) return today;
  return shiftDay(today, days);
}

export default function DateSelector({ selected, onSelect }: DateSelectorProps) {
  const yesterday = offset(-1);
  const today     = offset(0);
  const tomorrow  = offset(1);

  const options = [
    { label: '어제', value: yesterday },
    { label: '오늘', value: today },
    { label: '내일', value: tomorrow },
  ];

  return (
    <div className={styles.group}>
      {options.map((o) => (
        <button
          key={o.value}
          className={selected === o.value ? styles.btnActive : styles.btn}
          onClick={() => onSelect(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
