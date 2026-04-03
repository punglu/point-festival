import { useState, useEffect } from 'react';
import styles from '../UserDashboard.module.css';
import { DailyPointResponse, dashboardApi } from '../api/dashboardApi';
import ExpBar from './ExpBar';

interface Props {
  player: { id: number; name: string; role: string } | null;
  photo?: string | null;
  initialStatusMsg?: string;
  dailyPoint: DailyPointResponse | null;
  pendingPoints: number;
  levelThresholds: Record<string, number> | null;
  onStatClick?: (type: 'earned' | 'balance' | 'pending') => void;
}

export default function ProfileCard({
  player, photo, initialStatusMsg = '', dailyPoint, pendingPoints, levelThresholds, onStatClick,
}: Props) {
  const [statusMsg, setStatusMsg] = useState(initialStatusMsg);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  // 서버에서 로드된 초기값 반영
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

  return (
    <div className={styles.profileCard}>
      {/* 프로필 행: 아바타 + 이름 + ExpBar */}
      <div className={styles.profileRow}>
        {photo ? (
          <img src={photo} alt={player?.name ?? ''} className={styles.avatarImg} />
        ) : (
          <div className={styles.avatar}>
            {player?.name?.[0] ?? '?'}
          </div>
        )}
        <div className={styles.profileInfo}>
          <div className={styles.playerName}>{player?.name ?? '—'}</div>
          <ExpBar totalPoints={balance} levelThresholds={levelThresholds} />
        </div>
      </div>

      {/* 상태 메시지 */}
      <div className={styles.statusRow}>
        <input
          className={styles.statusInput}
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

      {/* 스탯 카드 3개 (Duolingo 3D) */}
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
          <div className={styles.statNumber}>{balance}P</div>
          <div className={styles.statLabel}>현재 보유</div>
        </button>
      </div>
    </div>
  );
}
