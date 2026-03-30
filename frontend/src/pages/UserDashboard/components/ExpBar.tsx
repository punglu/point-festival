import styles from '../UserDashboard.module.css';

interface ExpBarProps {
  totalPoints: number;
  levelThresholds: Record<string, number>;
}

export default function ExpBar({ totalPoints, levelThresholds }: ExpBarProps) {
  // 레벨 계산: thresholds 내림차순 순회
  const levels = Object.entries(levelThresholds)
    .map(([lv, pts]) => ({ level: Number(lv), points: pts }))
    .sort((a, b) => b.points - a.points);

  let currentLevel = 1;
  for (const { level, points } of levels) {
    if (totalPoints >= points) {
      currentLevel = level;
      break;
    }
  }

  // 현재 레벨 → 다음 레벨 진행률
  const currentThreshold = levelThresholds[String(currentLevel)] ?? 0;
  const nextLevel = currentLevel + 1;
  const nextThreshold = levelThresholds[String(nextLevel)] ?? null;

  let progressPercent = 100;
  if (nextThreshold !== null) {
    const range = nextThreshold - currentThreshold;
    const progress = totalPoints - currentThreshold;
    progressPercent = range > 0 ? Math.min(Math.round((progress / range) * 100), 100) : 100;
  }

  return (
    <div className={styles.expBarContainer}>
      <span className={styles.levelBadge}>Lv.{currentLevel}</span>
      <div className={styles.expBarTrack}>
        <div
          className={styles.expBarFill}
          style={{ width: `${progressPercent}%` }}
        />
      </div>
      <span className={styles.expBarText}>
        {nextThreshold !== null
          ? `${totalPoints - currentThreshold} / ${nextThreshold - currentThreshold}`
          : 'MAX'}
      </span>
    </div>
  );
}
