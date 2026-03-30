import { useState } from 'react';
import styles from '../AdminDashboard.module.css';
import { adminApi, PlayerItem } from '../api/adminApi';

interface Props {
  players: PlayerItem[];
  onRefresh: () => void;
}

interface EditState {
  name: string;
  status_msg: string;
  photo: string;
}

export default function PlayerManager({ players, onRefresh }: Props) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editState, setEditState] = useState<EditState>({ name: '', status_msg: '', photo: '' });
  const [loading, setLoading] = useState(false);

  const openEdit = (p: PlayerItem) => {
    setEditingId(p.id);
    setEditState({ name: p.name, status_msg: '', photo: '' });
  };

  const handleSave = async () => {
    if (!editingId) return;
    setLoading(true);
    try {
      await adminApi.updatePlayer(editingId, {
        name: editState.name || undefined,
        status_msg: editState.status_msg || undefined,
        photo: editState.photo || undefined,
      });
      setEditingId(null);
      onRefresh();
    } catch {
      alert('수정 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleLockToggle = async (p: PlayerItem) => {
    const action = p.is_locked ? '잠금 해제' : '잠금';
    if (!confirm(`${p.name}을(를) ${action}하시겠습니까?`)) return;
    try {
      await adminApi.lockPlayer(p.id, !p.is_locked);
      onRefresh();
    } catch {
      alert('처리 실패');
    }
  };

  return (
    <div className={styles.adminCard}>
      <div className={styles.adminCardTitle}>플레이어 관리</div>

      {players.map((p) => (
        <div key={p.id} className={styles.playerCard}>
          <div className={styles.playerAvatar}>👤</div>
          <div className={styles.playerInfo}>
            <div className={styles.playerName}>{p.name}</div>
            {p.is_locked && <div className={styles.playerLocked}>🔒 잠금됨</div>}
          </div>
          <div className={styles.missionActions}>
            <button className={`${styles.btnSecondary} ${styles.btnSm}`} onClick={() => openEdit(p)}>수정</button>
            <button
              className={`${p.is_locked ? styles.btnSuccess : styles.btnDanger} ${styles.btnSm}`}
              onClick={() => handleLockToggle(p)}
            >
              {p.is_locked ? '해제' : '잠금'}
            </button>
          </div>
        </div>
      ))}

      {editingId && (
        <div className={styles.modalOverlay} onClick={() => setEditingId(null)}>
          <div className={styles.modalBox} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalTitle}>플레이어 수정</div>
            <div className={styles.formGroup}>
              <label className={styles.formLabel}>이름</label>
              <input className={styles.formInput} value={editState.name} onChange={(e) => setEditState((s) => ({ ...s, name: e.target.value }))} />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.formLabel}>상태 메시지</label>
              <input className={styles.formInput} placeholder="상태 메시지" value={editState.status_msg} onChange={(e) => setEditState((s) => ({ ...s, status_msg: e.target.value }))} />
            </div>
            <button className={styles.btnPrimary} style={{ width: '100%' }} onClick={handleSave} disabled={loading}>
              {loading ? '저장 중...' : '저장'}
            </button>
            <button className={styles.modalClose} onClick={() => setEditingId(null)}>닫기</button>
          </div>
        </div>
      )}
    </div>
  );
}
