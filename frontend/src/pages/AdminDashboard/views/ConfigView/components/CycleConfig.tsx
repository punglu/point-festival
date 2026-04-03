import styles from './CycleConfig.module.css';

interface CycleData { period: string; start_day: string; end_time: string; }
const PERIODS  = ['weekly', 'biweekly', 'monthly'] as const;
const WEEKDAYS = ['월', '화', '수', '목', '금', '토', '일'] as const;
const PERIOD_LABELS: Record<string, string> = { weekly: '주간', biweekly: '격주', monthly: '월간' };

interface Props {
  value:    string | null;
  onChange: (value: string) => void;
}

function parse(value: string | null): CycleData {
  try { if (value) return JSON.parse(value); } catch { /* ignore */ }
  return { period: 'weekly', start_day: '월', end_time: '23:59' };
}

export default function CycleConfig({ value, onChange }: Props) {
  const data = parse(value);

  const update = (patch: Partial<CycleData>) => {
    onChange(JSON.stringify({ ...data, ...patch }));
  };

  return (
    <div className={styles.section}>
      <div className={styles.sectionTitle}>포인트 사이클 설정</div>

      <div className={styles.fieldGroup}>
        <div className={styles.label}>기간</div>
        <div className={styles.segmentRow}>
          {PERIODS.map((p) => (
            <button
              key={p}
              className={data.period === p ? styles.segBtnActive : styles.segBtn}
              onClick={() => update({ period: p })}
            >
              {PERIOD_LABELS[p]}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.fieldGroup}>
        <div className={styles.label}>시작 요일</div>
        <div className={styles.segmentRow}>
          {WEEKDAYS.map((d) => (
            <button
              key={d}
              className={data.start_day === d ? styles.segBtnActive : styles.segBtn}
              onClick={() => update({ start_day: d })}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.fieldGroup}>
        <div className={styles.label}>종료 시각</div>
        <input
          type="time"
          className={styles.input}
          value={data.end_time}
          onChange={(e) => update({ end_time: e.target.value })}
        />
      </div>
    </div>
  );
}
