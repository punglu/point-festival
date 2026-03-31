import { useState } from 'react';
import styles from '../UserDashboard.module.css';
import { DailyPointResponse, dashboardApi } from '../api/dashboardApi';
import ExpBar from './ExpBar';

interface Props {
  player: { id: number; name: string; role: string } | null;
  dailyPoint: DailyPointResponse | null;
  pendingPoints: number;
  levelThresholds: Record<string, number> | null;
  onStatClick?: (type: 'earned' | 'balance' | 'pending') => void;
}

export default function ProfileCard({
  player, dailyPoint, pendingPoints, levelThresholds, onStatClick,
}: Props) {
  const [statusMsg, setStatusMsg] = useState('');
  const [saving, setSaving] = useState(false);

  const handleStatusSave = async () => {
    if (!player || !statusMsg.trim()) return;
    setSaving(true);
    try {
      await dashboardApi.updateStatusMsg(player.id, statusMsg.trim());
    } catch {
      // 저장 실패 시 무시
    } finally {
      setSaving(false);
    }
  };

  const earned = dailyPoint?.earned ?? 0;
  const balance = dailyPoint?.balance ?? 0;

  return (
    <div className={styles.profileCard}>
      <div className={styles.profileHeader}>
        <div className={styles.profilePhotoPlaceholder}>
          {player?.name?.[0] ?? '?'}
        </div>
        <div>
          <div className={styles.profileName}>{player?.name ?? '—'}</div>
          <div className={styles.profileRole}>
            {player?.role === 'admin' ? '관리자' : '플레이어'}
          </div>
        </div>
      </div>

      <input
        className={styles.statusInput}
        placeholder="상태 메시지를 입력하세요..."
        value={statusMsg}
        onChange={e => setStatusMsg(e.target.value)}
        onBlur={handleStatusSave}
        disabled={saving}
        maxLength={200}
      />

      <div className={styles.statRow}>
        <button className={styles.statPill} onClick={() => onStatClick?.('earned')}>
          <div className={styles.statLabel}>오늘 획득</div>
          <div className={`${styles.statValue} ${styles.statEarned}`}>{earned}P</div>
        </button>
        <button className={styles.statPill} onClick={() => onStatClick?.('balance')}>
          <div className={styles.statLabel}>현재 보유</div>
          <div className={`${styles.statValue} ${styles.statBalance}`}>{balance}P</div>
        </button>
        <button className={styles.statPill} onClick={() => onStatClick?.('pending')}>
          <div className={styles.statLabel}>남은 미션</div>
          <div className={`${styles.statValue} ${styles.statPending}`}>{pendingPoints}P</div>
        </button>
      </div>

      <ExpBar totalPoints={balance} levelThresholds={levelThresholds} />
    </div>
  );
}
