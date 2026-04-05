import { useState } from 'react';
import styles from './PlayerView.module.css';
import { usePlayerView } from './hooks/usePlayerView';
import PlayerProfileCard from './components/PlayerProfileCard';
import LoginLogTable from './components/LoginLogTable';
import PinChangeModal from './components/PinChangeModal';
import PhotoUploadModal from './components/PhotoUploadModal';
import AddPlayerModal from './components/AddPlayerModal';
import { adminApi } from '../../api/adminApi';
import type { Player } from '../../types/admin.types';

export default function PlayerView() {
  const {
    players, missions, loginLogs, loading,
    changePin, updatePlayer, createPlayer, deletePlayer, achievementRate, reload,
  } = usePlayerView();

  const [pinTarget,    setPinTarget]    = useState<Player | null>(null);
  const [photoTarget,  setPhotoTarget]  = useState<Player | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

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
    </div>
  );
}
