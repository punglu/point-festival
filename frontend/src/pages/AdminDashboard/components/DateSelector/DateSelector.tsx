import styles from './DateSelector.module.css';

interface DateSelectorProps {
  selected: string;
  onSelect: (date: string) => void;
}

function offset(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
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
