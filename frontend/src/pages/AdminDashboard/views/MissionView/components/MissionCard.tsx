import styles from './MissionCard.module.css';
import { MISSION_STATUS_MAP } from '../../../constants/admin.constants';
import type { Mission, Player } from '../../../types/admin.types';

interface Props {
  mission: Mission;
  players: Player[];
  onApprove: (m: Mission) => void;
  onReject:  (id: number) => void;
  onDelete:  (id: number) => void;
  onEdit:    () => void;
  onUndoComplete: (id: number) => void;
}

const BORDER_CLASS: Record<string, string> = {
  active:           styles.borderActive,
  pending_approval: styles.borderPendingApproval,
  completed:        styles.borderCompleted,
  failed:           styles.borderFailed,
  rejected:         styles.borderRejected,
  proposed:         styles.borderProposed,
};

export default function MissionCard({ mission, players, onApprove, onReject, onDelete, onEdit, onUndoComplete }: Props) {
  const player     = players.find((p) => p.id === mission.player_id);
  const statusInfo = MISSION_STATUS_MAP[mission.status];
  const borderCls  = BORDER_CLASS[mission.status] ?? styles.borderFailed;
  const isCompleted = mission.status === 'completed';

  return (
    <div className={`${styles.card} ${borderCls}`}>
      <div className={styles.topRow}>
        <span className={isCompleted ? styles.missionTextCompleted : styles.missionText}>
          {mission.text}
        </span>
        {statusInfo && (
          <span
            className={styles.statusBadge}
            style={{ background: statusInfo.bgColor, color: statusInfo.color }}
          >
            {statusInfo.label}
          </span>
        )}
      </div>

      <div className={styles.metaRow}>
        {player && <span className={styles.playerName}>{player.name}</span>}
        <span className={styles.pointBadge}>{mission.point}pt</span>
      </div>

      {mission.proposal_reason && (
        <div className={styles.proposalReason}>💬 {mission.proposal_reason}</div>
      )}

      <div className={styles.actions}>
        {(mission.status === 'pending_approval' || mission.status === 'proposed') && (
          <>
            <button className={styles.btnApprove} onClick={() => onApprove(mission)}>승인</button>
            <button className={styles.btnReject}  onClick={() => onReject(mission.id)}>거절</button>
          </>
        )}
        {mission.status === 'active' && (
          <>
            <button className={styles.btnEdit}   onClick={onEdit}>편집</button>
            <button className={styles.btnDelete} onClick={() => onDelete(mission.id)}>삭제</button>
          </>
        )}
        {mission.status === 'completed' && (
          <button className={styles.btnUndo} onClick={() => onUndoComplete(mission.id)}>완료 취소</button>
        )}
      </div>
    </div>
  );
}
