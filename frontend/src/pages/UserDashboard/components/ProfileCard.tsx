import { useState, useEffect } from 'react';
import styles from '../UserDashboard.module.css';
import { DailyPointResponse, dashboardApi } from '../api/dashboardApi';
import AppIcon from '../../../shared/components/AppIcon';

interface Props {
  player: { id: number; name: string; role: string } | null;
  photo?: string | null;
  initialStatusMsg?: string;
  dailyPoint: DailyPointResponse | null;
  pendingPoints: number;
  levelThresholds: Record<string, number> | null;
  totalEarned?: number;
  onStatClick?: (type: 'earned' | 'balance' | 'pending') => void;
}

function calcLevel(totalPoints: number, levelThresholds: Record<string, number> | null): {
  level: number;
  progressPercent: number;
  nextThreshold: number | null;
} {
  if (!levelThresholds) return { level: 1, progressPercent: 0, nextThreshold: null };
  const levels = Object.entries(levelThresholds)
    .map(([lv, pts]) => ({ level: Number(lv), points: pts }))
    .sort((a, b) => b.points - a.points);
  let currentLevel = 1;
  for (const { level, points } of levels) {
    if (totalPoints >= points) { currentLevel = level; break; }
  }
  const currentThreshold = levelThresholds[String(currentLevel)] ?? 0;
  const nextThreshold = levelThresholds[String(currentLevel + 1)] ?? null;
  let progressPercent = 100;
  if (nextThreshold !== null) {
    const range = nextThreshold - currentThreshold;
    const progress = totalPoints - currentThreshold;
    progressPercent = range > 0 ? Math.min(Math.round((progress / range) * 100), 100) : 100;
  }
  return { level: currentLevel, progressPercent, nextThreshold };
}

export default function ProfileCard({
  player, photo, initialStatusMsg = '', dailyPoint, pendingPoints, levelThresholds, totalEarned = 0, onStatClick,
}: Props) {
  const [statusMsg, setStatusMsg] = useState(initialStatusMsg);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setStatusMsg(initialStatusMsg);
  }, [initialStatusMsg]);

  const handleStatusSave = async () => {
    if (!player) return;
    setSaving(true);
    try {
      await dashboardApi.updateStatusMsg(player.id, statusMsg.trim());
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // 저장 실패 시 무시
    } finally {
      setSaving(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
      handleStatusSave();
    }
  };

  const earned = dailyPoint?.earned ?? 0;
  const balance = dailyPoint?.balance ?? 0;
  const { level, progressPercent, nextThreshold } = calcLevel(totalEarned, levelThresholds);

  return (
    <div className={styles.profileCard}>
      {/* Row 1: 아바타 + 말풍선 상태메시지 */}
      <div className={styles.profileRow1}>
        {photo ? (
          <img src={photo} alt={player?.name ?? ''} className={styles.profileAvatarLg} />
        ) : (
          <div className={styles.profileAvatarLgInitial}>
            {player?.name?.[0] ?? '?'}
          </div>
        )}
        <div className={styles.profileBubbleWrap}>
          <input
            className={styles.profileBubbleInput}
            placeholder="상태 메시지를 입력하세요..."
            value={statusMsg}
            onChange={e => setStatusMsg(e.target.value)}
            onBlur={handleStatusSave}
            onKeyDown={handleKeyDown}
            disabled={saving}
            maxLength={200}
          />
          {saved && <span className={styles.statusSaved}>저장됨</span>}
        </div>
      </div>

      {/* Row 2: 이름 + 레벨 + EXP바 + 미션 갯수 */}
      <div className={styles.profileRow2}>
        <span className={styles.profileNameInline}>{player?.name ?? '—'}</span>
        <span className={styles.profileLvBadge}>Lv.{level}</span>
        <div className={styles.profileExpInline}>
          <div className={styles.profileExpTrackInline}>
            <div
              className={styles.profileExpFillInline}
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
        <span className={styles.profileMissionCount}>
          {totalEarned}P / {nextThreshold !== null ? `${nextThreshold}P` : 'MAX'}
        </span>
      </div>

      {/* 스탯 카드 3개 */}
      <div className={styles.statGrid}>
        <button className={`${styles.statCard} ${styles.statCardCompleted}`} onClick={() => onStatClick?.('earned')}>
          <div className={styles.statNumber}>{earned}P</div>
          <div className={styles.statLabel}>오늘 획득</div>
        </button>
        <button className={`${styles.statCard} ${styles.statCardRemaining}`} onClick={() => onStatClick?.('pending')}>
          <div className={styles.statNumber}>{pendingPoints}P</div>
          <div className={styles.statLabel}>남은 미션</div>
        </button>
        <button className={`${styles.statCard} ${styles.statCardPoints}`} onClick={() => onStatClick?.('balance')}>
          <div className={styles.statNumber}><AppIcon name="gem" size={16} /> {balance}P</div>
          <div className={styles.statLabel}>현재 보유</div>
        </button>
      </div>
    </div>
  );
}
