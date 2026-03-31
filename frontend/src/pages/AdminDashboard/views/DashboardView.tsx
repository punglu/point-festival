import { useEffect, useState } from 'react';
import styles from './DashboardView.module.css';
import { useAdminFilter } from '../hooks/useAdminFilter';
import { dashboardApi } from '../../UserDashboard/api/dashboardApi';
import type { MissionResponse, DailyPointResponse } from '../../UserDashboard/api/dashboardApi';

export default function DashboardView() {
  const { selectedPlayerId, selectedDate, players } = useAdminFilter();
  const [missions, setMissions] = useState<MissionResponse[]>([]);
  const [dailyPoint, setDailyPoint] = useState<DailyPointResponse | null>(null);

  useEffect(() => {
    if (!selectedPlayerId) return;
    const abortController = new AbortController();
    dashboardApi.fetchDayData(selectedPlayerId, selectedDate, abortController.signal)
      .then((res) => {
        if (!abortController.signal.aborted) {
          setMissions(res.missions);
          setDailyPoint(res.dailyPoint ?? null);
        }
      })
      .catch(() => {});
    return () => abortController.abort();
  }, [selectedPlayerId, selectedDate]);

  const selectedPlayer = players.find((p) => p.id === selectedPlayerId);
  const completed = missions.filter((m) => m.status === 'completed').length;
  const pending = missions.filter((m) => m.status === 'pending_approval' || m.status === 'proposed').length;
  const total = missions.length;

  return (
    <div className={styles.dashboard}>
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>
          {selectedPlayer ? `${selectedPlayer.name}의 현황` : '플레이어를 선택하세요'}
        </h2>
        <p className={styles.dateLine}>{selectedDate}</p>
      </div>

      <div className={styles.statGrid}>
        <div className={styles.statCard}>
          <span className={styles.statIcon}>💎</span>
          <span className={styles.statValue}>{dailyPoint?.balance ?? 0}</span>
          <span className={styles.statLabel}>포인트 잔액</span>
        </div>
        <div className={styles.statCard}>
          <span className={styles.statIcon}>✅</span>
          <span className={styles.statValue}>{completed}</span>
          <span className={styles.statLabel}>완료 미션</span>
        </div>
        <div className={styles.statCard}>
          <span className={styles.statIcon}>⏳</span>
          <span className={styles.statValue}>{pending}</span>
          <span className={styles.statLabel}>대기 미션</span>
        </div>
        <div className={styles.statCard}>
          <span className={styles.statIcon}>📋</span>
          <span className={styles.statValue}>{total}</span>
          <span className={styles.statLabel}>전체 미션</span>
        </div>
      </div>

      {total > 0 && (
        <div className={styles.section}>
          <h3 className={styles.subTitle}>오늘의 미션</h3>
          <ul className={styles.missionList}>
            {missions.map((m) => (
              <li key={m.id} className={`${styles.missionItem} ${styles[`status_${m.status}`] ?? ''}`}>
                <span className={styles.missionStatus}>
                  {m.status === 'completed' ? '✅'
                    : m.status === 'pending_approval' || m.status === 'proposed' ? '⏳'
                    : m.status === 'active' ? '🎮'
                    : '❌'}
                </span>
                <span className={styles.missionText}>{m.text}</span>
                <span className={styles.missionPoint}>{m.point}p</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
