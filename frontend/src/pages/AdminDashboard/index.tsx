import styles from './AdminDashboard.module.css';
import { useAdmin } from './hooks/useAdmin';
import AdminNav from './components/AdminNav';
import MissionManager from './components/MissionManager';
import PointManager from './components/PointManager';
import CheerEditor from './components/CheerEditor';
import PlayerManager from './components/PlayerManager';
import NotificationManager from './components/NotificationManager';
import FeedbackViewer from './components/FeedbackViewer';
import ConfigManager from './components/ConfigManager';
import { PlayerItem } from './api/adminApi';

export default function AdminDashboard() {
  const {
    players,
    selectedPlayerId,
    selectedDate,
    activeTab,
    activeMoreTab,
    loading,
    setSelectedPlayerId,
    setSelectedDate,
    setActiveTab,
    setActiveMoreTab,
  } = useAdmin();

  const adminPlayers: PlayerItem[] = players.map((p) => ({
    id: p.id,
    name: p.name,
    role: p.role,
    last_login: p.last_login,
    is_locked: false,
  }));

  return (
    <div className={styles.adminWrapper}>
      <AdminNav activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className={styles.adminContent}>
        {/* 공통 선택기 (미션/포인트) */}
        {(activeTab === 'missions' || activeTab === 'points') && (
          <div className={styles.adminSelectors}>
            <select
              className={styles.adminSelect}
              value={selectedPlayerId ?? ''}
              onChange={(e) => setSelectedPlayerId(Number(e.target.value))}
            >
              {loading ? (
                <option>로딩 중...</option>
              ) : (
                players.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))
              )}
            </select>
            <input
              className={styles.adminDateInput}
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
          </div>
        )}

        {/* 탭 콘텐츠 */}
        {activeTab === 'missions' && (
          <MissionManager playerId={selectedPlayerId} selectedDate={selectedDate} />
        )}

        {activeTab === 'points' && (
          <PointManager playerId={selectedPlayerId} selectedDate={selectedDate} />
        )}

        {activeTab === 'cheer' && (
          <CheerEditor selectedDate={selectedDate} />
        )}

        {activeTab === 'players' && (
          <PlayerManager
            players={adminPlayers}
            onRefresh={() => window.location.reload()}
          />
        )}

        {activeTab === 'more' && (
          <>
            {/* 더보기 서브탭 */}
            <div className={styles.adminSelectors}>
              {(['notifications', 'feedbacks', 'configs'] as const).map((t) => (
                <button
                  key={t}
                  className={`${styles.adminNavTab} ${activeMoreTab === t ? styles.adminNavTabActive : ''}`}
                  onClick={() => setActiveMoreTab(t)}
                >
                  {t === 'notifications' ? '알림' : t === 'feedbacks' ? '피드백' : '설정'}
                </button>
              ))}
            </div>

            {activeMoreTab === 'notifications' && (
              <NotificationManager playerId={selectedPlayerId} />
            )}
            {activeMoreTab === 'feedbacks' && (
              <>
                <div className={styles.adminSelectors}>
                  <select
                    className={styles.adminSelect}
                    value={selectedPlayerId ?? ''}
                    onChange={(e) => setSelectedPlayerId(Number(e.target.value))}
                  >
                    {players.map((p) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                  <input
                    className={styles.adminDateInput}
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                  />
                </div>
                <FeedbackViewer playerId={selectedPlayerId} selectedDate={selectedDate} />
              </>
            )}
            {activeMoreTab === 'configs' && <ConfigManager />}
          </>
        )}
      </div>
    </div>
  );
}
