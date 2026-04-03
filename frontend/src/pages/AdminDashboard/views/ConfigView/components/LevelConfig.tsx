import styles from './LevelConfig.module.css';

interface Props {
  value:    string | null;  // JSON: [0, 50, 100, 200, 350, 500] — index 0 is always 0 (Lv.1)
  onChange: (value: string) => void;
}

const DEFAULT = [0, 50, 100, 200, 350, 500];

function parse(value: string | null): number[] {
  try {
    if (value) {
      const raw = JSON.parse(value);
      // 신 포맷: 배열 [0, 50, 100, 200, 350, 500]
      if (Array.isArray(raw) && raw.length >= 2) return raw;
      // 구 포맷: 객체 {"1":0,"2":50,...} — 키=레벨번호, 값=임계치
      if (typeof raw === 'object' && raw !== null) {
        const sorted = Object.entries(raw as Record<string, number>)
          .sort(([a], [b]) => Number(a) - Number(b))
          .map(([, v]) => Number(v));
        // 6개 미만이면 마지막 값 * 2로 채움
        while (sorted.length < 6) sorted.push((sorted[sorted.length - 1] ?? 0) * 2 || 1000);
        return sorted.slice(0, 6);
      }
    }
  } catch { /* ignore */ }
  return DEFAULT;
}

export default function LevelConfig({ value, onChange }: Props) {
  const thresholds = parse(value);
  // Show Lv.2~Lv.6 (indices 1-5); Lv.1 starts at 0 and is not editable
  const editable = thresholds.slice(1);

  const updateAt = (i: number, v: number) => {
    const next = [...thresholds];
    next[i + 1] = v;
    onChange(JSON.stringify(next));
  };

  return (
    <div className={styles.section}>
      <div className={styles.sectionTitle}>레벨 임계치 (pt)</div>
      <div className={styles.grid}>
        {editable.map((val, i) => (
          <div key={i} className={styles.levelItem}>
            <div className={styles.levelLabel}>Lv.{i + 2}</div>
            <input
              type="number"
              className={styles.input}
              value={val}
              min={0}
              onChange={(e) => updateAt(i, Number(e.target.value))}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
