import { useState } from 'react';
import styles from './DashboardModal.module.css';
import AdminModal from '../../../components/AdminModal/AdminModal';
import PlayerTab from '../../../components/PlayerTab/PlayerTab';
import type { Mission, Player } from '../../../types/admin.types';

interface Props {
  open:    boolean;
  onClose: () => void;
  missions: Mission[];
  players:  Player[];
  onApprove: (id: number) => Promise<void>;
  onReject:  (id: number, reason: string) => Promise<void>;
}

export default function PendingApprovalModal({ open, onClose, missions, players, onApprove, onReject }: Props) {
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
  const [rejectingId,    setRejectingId]    = useState<number | null>(null);
  const [rejectReason,   setRejectReason]   = useState('');

  const pending = missions
    .filter((m) => m.status === 'pending_approval' && (selectedPlayer === null || m.player_id === selectedPlayer))
    .sort((a, b) => b.created_at.localeCompare(a.created_at));

  const handleApprove = async (id: number) => {
    await onApprove(id);
  };

  const handleReject = async (id: number) => {
    await onReject(id, rejectReason);
    setRejectingId(null);
    setRejectReason('');
  };

  return (
    <AdminModal open={open} onClose={onClose} title="승인 대기 미션" width={520}>
      <PlayerTab players={players} selected={selectedPlayer} onSelect={setSelectedPlayer} />
      <div className={styles.listBody}>
        {pending.length === 0 ? (
          <div className={styles.empty}>승인 대기 미션이 없습니다 ✓</div>
        ) : (
          pending.map((m) => {
            const player = players.find((p) => p.id === m.player_id);
            return (
              <div key={m.id} className={styles.pendingRow}>
                <div className={styles.pendingInfo}>
                  <span className={styles.missionText}>{m.text}</span>
                  <div className={styles.pendingMeta}>
                    <span className={styles.playerBadge}>{player?.name ?? '?'}</span>
                    <span className={styles.pointBadge}>{m.point}pt</span>
                    <span className={styles.dateMeta}>{m.date}</span>
                  </div>
                </div>
                {rejectingId === m.id ? (
                  <div className={styles.rejectForm}>
                    <input
                      className={styles.rejectInput}
                      placeholder="거절 사유 (선택)"
                      value={rejectReason}
                      onChange={(e) => setRejectReason(e.target.value)}
                    />
                    <button className={styles.btnConfirmReject} onClick={() => handleReject(m.id)}>확인</button>
                    <button className={styles.btnCancel} onClick={() => setRejectingId(null)}>취소</button>
                  </div>
                ) : (
                  <div className={styles.pendingActions}>
                    <button className={styles.btnApprove} onClick={() => handleApprove(m.id)}>승인</button>
                    <button className={styles.btnReject} onClick={() => { setRejectingId(m.id); setRejectReason(''); }}>거절</button>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </AdminModal>
  );
}
