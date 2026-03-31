import { useState, useEffect, useCallback } from 'react';
import styles from '../AdminDashboard.module.css';
import { adminApi, MissionItem } from '../api/adminApi';
import { dashboardApi } from '../../UserDashboard/api/dashboardApi';
import MissionCloneModal from './MissionCloneModal';

interface Props {
  playerId: number | null;
  selectedDate: string;
}

export default function MissionManager({ playerId, selectedDate }: Props) {
  const [missions, setMissions] = useState<MissionItem[]>([]);
  const [showCloneModal, setShowCloneModal] = useState(false);
  const [newText, setNewText] = useState('');
  const [newPoint, setNewPoint] = useState(10);
  const [loading, setLoading] = useState(false);

  const loadMissions = useCallback(async () => {
    if (!playerId) return;
    const abortController = new AbortController();
    setLoading(true);
    try {
      const res = await dashboardApi.fetchDayData(playerId, selectedDate, abortController.signal);
      if (!abortController.signal.aborted) setMissions(res.missions);
    } catch {
      // ignore abort
    } finally {
      if (!abortController.signal.aborted) setLoading(false);
    }
  }, [playerId, selectedDate]);

  useEffect(() => {
    const abortController = new AbortController();
    if (!playerId) return;
    setLoading(true);
    dashboardApi.fetchDayData(playerId, selectedDate, abortController.signal)
      .then((res) => { if (!abortController.signal.aborted) setMissions(res.missions); })
      .catch(() => {})
      .finally(() => { if (!abortController.signal.aborted) setLoading(false); });
    return () => abortController.abort();
  }, [playerId, selectedDate]);

  const handleAdd = async () => {
    if (!playerId || !newText.trim()) return;
    await adminApi.createMission({
      player_id: playerId,
      date: selectedDate,
      text: newText.trim(),
      point: newPoint,
      status: 'active',
      sender: null,
      msg: null,
      sort_order: missions.length,
    });
    setNewText('');
    setNewPoint(10);
    loadMissions();
  };

  const handleStatusChange = async (missionId: number, status: string) => {
    await adminApi.updateMission(missionId, { status });
    loadMissions();
  };

  const handleDelete = async (missionId: number) => {
    if (!confirm('미션을 삭제하시겠습니까?')) return;
    await adminApi.deleteMission(missionId);
    loadMissions();
  };

  const prevDate = new Date(selectedDate);
  prevDate.setDate(prevDate.getDate() - 1);
  const prevDateStr = prevDate.toISOString().slice(0, 10);

  return (
    <div className={styles.adminCard}>
      <div className={styles.adminCardTitle}>
        미션 관리
        <button
          className={`${styles.btnSecondary} ${styles.btnSm} ${styles.floatRight}`}
          onClick={() => setShowCloneModal(true)}
        >
          전일 복제
        </button>
      </div>

      {/* 미션 추가 폼 */}
      <div className={styles.adminSelectors}>
        <input
          className={`${styles.formInput} ${styles.flex3}`}
          placeholder="미션 내용"
          value={newText}
          onChange={(e) => setNewText(e.target.value)}
        />
        <input
          className={`${styles.formInput} ${styles.flex1}`}
          type="number"
          placeholder="P"
          value={newPoint}
          onChange={(e) => setNewPoint(Number(e.target.value))}
          min={0}
        />
        <button className={styles.btnPrimary} onClick={handleAdd}>추가</button>
      </div>

      {/* 미션 목록 */}
      {loading ? (
        <div className={styles.emptyMsg}>로딩 중...</div>
      ) : missions.length === 0 ? (
        <div className={styles.emptyMsg}>미션이 없습니다.</div>
      ) : (
        missions.map((m) => (
          <div key={m.id} className={styles.missionRow}>
            <div className={styles.flex1}>
              <div className={styles.missionText}>{m.text}</div>
              <div className={styles.missionMetaRow}>
                <span className={styles.missionStatus}>{m.status}</span>
                <span className={styles.missionPoint}>{m.point}P</span>
              </div>
            </div>
            <div className={styles.missionActions}>
              {m.status === 'active' && (
                <>
                  <button className={`${styles.btnSuccess} ${styles.btnSm}`} onClick={() => handleStatusChange(m.id, 'completed')}>완료</button>
                  <button className={`${styles.btnDanger} ${styles.btnSm}`} onClick={() => handleStatusChange(m.id, 'failed')}>실패</button>
                </>
              )}
              {m.status === 'pending_approval' && (
                <>
                  <button className={`${styles.btnSuccess} ${styles.btnSm}`} onClick={() => handleStatusChange(m.id, 'completed')}>승인</button>
                  <button className={`${styles.btnDanger} ${styles.btnSm}`} onClick={() => handleStatusChange(m.id, 'rejected')}>거절</button>
                </>
              )}
              {m.status === 'proposed' && (
                <>
                  <button className={`${styles.btnPrimary} ${styles.btnSm}`} onClick={() => handleStatusChange(m.id, 'active')}>활성화</button>
                  <button className={`${styles.btnDanger} ${styles.btnSm}`} onClick={() => handleStatusChange(m.id, 'rejected')}>거절</button>
                </>
              )}
              {(m.status === 'completed' || m.status === 'failed' || m.status === 'rejected') && (
                <button className={`${styles.btnSecondary} ${styles.btnSm}`} onClick={() => handleStatusChange(m.id, 'active')}>재활성</button>
              )}
              <button className={`${styles.btnDanger} ${styles.btnSm}`} onClick={() => handleDelete(m.id)}>삭제</button>
            </div>
          </div>
        ))
      )}

      {showCloneModal && playerId && (
        <MissionCloneModal
          playerId={playerId}
          sourceDate={prevDateStr}
          targetDate={selectedDate}
          sourceMissions={missions}
          onClose={() => setShowCloneModal(false)}
          onCloned={loadMissions}
        />
      )}
    </div>
  );
}
