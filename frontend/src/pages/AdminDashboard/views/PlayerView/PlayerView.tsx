import { useState } from 'react';
import styles from './PlayerView.module.css';
import { usePlayerView } from './hooks/usePlayerView';
import PlayerProfileCard from './components/PlayerProfileCard';
import LoginLogTable from './components/LoginLogTable';
import PinChangeModal from './components/PinChangeModal';
import PhotoUploadModal from './components/PhotoUploadModal';
import AddPlayerModal from './components/AddPlayerModal';
import { adminApi } from '../../api/adminApi';
import { UserManagementDetailScreen } from '../../../../screens/admin/UserManagementDetail';
import type { UserManagementDetailModel } from '../../../../screens/admin/UserManagementDetail';
import type { Player } from '../../types/admin.types';

export default function PlayerView() {
  const {
    players, missions, loginLogs, loading,
    changePin, updatePlayer, createPlayer, deletePlayer, achievementRate, reload,
  } = usePlayerView();

  const [pinTarget,    setPinTarget]    = useState<Player | null>(null);
  const [photoTarget,  setPhotoTarget]  = useState<Player | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [detailTarget, setDetailTarget] = useState<Player | null>(null);

  const handleToggleLock = async (player: Player) => {
    try {
      await adminApi.lockPlayer(player.id, !player.is_locked);
      reload();
    } catch { /* silent */ }
  };

  const handleToggleDashboardVisibility = async (player: Player) => {
    try {
      await adminApi.setPlayerVisibility(player.id, { is_dashboard_visible: !player.is_dashboard_visible });
      reload();
    } catch { /* silent */ }
  };

  // canonical 2a (사용자 관리 상세) real-data adapter. 보유 포인트/누적 획득/
  // 교환 횟수/레벨/가입일/알림/보호자 승인은 Admin Player API에 실 필드가 없어
  // (TRUE_FUNCTIONAL_GAP) "—"로 disclosed; 나머지는 실제 데이터다.
  const toDetailModel = (player: Player): UserManagementDetailModel => {
    const playerMissions = missions.filter((m) => m.player_id === player.id);
    return {
      name: player.name,
      roleLabel: player.role === 'player' ? '자녀' : player.role,
      levelLabel: '—',
      joinedLabel: '—',
      lastActiveLabel: player.last_login ? new Date(player.last_login).toLocaleString('ko-KR') : '-',
      isActive: !player.is_locked,
      pointsLabel: '—',
      totalEarnedLabel: '—',
      completedMissionsLabel: `${playerMissions.filter((m) => m.status === 'completed').length}개`,
      redeemCountLabel: '—',
      pinStatusLabel: '설정됨',
      notificationLabel: '—',
      guardianApprovalLabel: '—',
      recentMissions: playerMissions
        .slice()
        .sort((a, b) => b.updated_at.localeCompare(a.updated_at))
        .slice(0, 5)
        .map((m) => ({ name: m.text, status: m.status === 'completed' ? '완료' : m.status === 'active' ? '진행 중' : m.status })),
    };
  };

  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <h1 className={styles.title}>플레이어 관리</h1>
        <button className={styles.btnPrimary} onClick={() => setShowAddModal(true)}>
          + 플레이어 추가
        </button>
      </div>

      {loading ? (
        <div className={styles.loading}>로딩 중...</div>
      ) : (
        <>
          <div className={styles.grid}>
            {players.map((p, i) => (
              <PlayerProfileCard
                key={p.id}
                player={p}
                index={i}
                achievementRate={achievementRate(p.id)}
                totalMissions={missions.filter((m) => m.player_id === p.id).length}
                onChangePin={() => setPinTarget(p)}
                onChangePhoto={() => setPhotoTarget(p)}
                onToggleLock={() => handleToggleLock(p)}
                onToggleDashboardVisibility={() => handleToggleDashboardVisibility(p)}
                onDelete={() => deletePlayer(p.id)}
                onOpenDetail={() => setDetailTarget(p)}
              />
            ))}
          </div>

          <LoginLogTable logs={loginLogs} players={players} />
        </>
      )}

      {pinTarget && (
        <PinChangeModal
          open={true}
          onClose={() => setPinTarget(null)}
          player={pinTarget}
          onSave={(pin) => changePin(pinTarget.id, pin)}
        />
      )}

      {photoTarget && (
        <PhotoUploadModal
          open={true}
          onClose={() => setPhotoTarget(null)}
          player={photoTarget}
          onSave={(photo) => updatePlayer(photoTarget.id, { photo })}
        />
      )}

      <AddPlayerModal
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={createPlayer}
      />

      {detailTarget && (
        <div className={styles.detailOverlay} data-testid="admin-user-detail-overlay">
          <UserManagementDetailScreen
            embedded
            model={toDetailModel(detailTarget)}
            onClose={() => setDetailTarget(null)}
            onToggleLock={() => { void handleToggleLock(detailTarget); setDetailTarget(null); }}
          />
        </div>
      )}
    </div>
  );
}
