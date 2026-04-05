import styles from './MissionCard.module.css';
import { MISSION_STATUS_MAP } from '../../../constants/admin.constants';
import type { Mission, Player } from '../../../types/admin.types';
import AppIcon from '../../../../../shared/components/AppIcon';

interface Props {
  mission: Mission;
  players: Player[];
  onApprove:      (m: Mission) => void;
  onReject:       (id: number) => void;
  onDelete:       (id: number, groupId?: string | null) => void;
  onEdit:         () => void;
  onEditTemplate: (m: Mission) => void;
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

function formatTime(isoStr: string): string {
  const d = new Date(isoStr);
  const h = d.getHours();
  const m = String(d.getMinutes()).padStart(2, '0');
  const ampm = h < 12 ? '오전' : '오후';
  const h12 = h % 12 || 12;
  return `${ampm} ${h12}:${m}`;
}

export default function MissionCard({ mission, players, onApprove, onReject, onDelete, onEdit, onEditTemplate, onUndoComplete }: Props) {
  const player     = players.find((p) => p.id === mission.player_id);
  const statusInfo = MISSION_STATUS_MAP[mission.status];
  const borderCls  = BORDER_CLASS[mission.status] ?? styles.borderFailed;
  const isCompleted = mission.status === 'completed';

  // 메타 항목 구성 (있는 것만)
  const metaItems: string[] = [];
  if (mission.sender) metaItems.push(mission.sender);
  if (mission.created_at) metaItems.push(formatTime(mission.created_at));

  return (
    <div className={`${styles.card} ${borderCls}`}>
      <div className={styles.missionCard}>

        {/* 좌측 영역 */}
        <div className={styles.cardLeft}>
          {/* Row 1: 플레이어뱃지 + 미션명 + 상태태그 */}
          <div className={styles.topRow}>
            {player && <span className={styles.playerName}>{player.name}</span>}
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

          {/* Row 2: 메타 정보 */}
          {metaItems.length > 0 && (
            <div className={styles.cardMeta}>
              {metaItems.map((item, i) => (
                <span key={i}>
                  {i > 0 && <span className={styles.metaDot}>·</span>}
                  {item}
                </span>
              ))}
            </div>
          )}

          {mission.proposal_reason && (
            <div className={styles.proposalReason}>💬 {mission.proposal_reason}</div>
          )}

          {/* Row 3: 액션 버튼 */}
          <div className={styles.actions}>
            {(mission.status === 'pending_approval' || mission.status === 'proposed') && (
              <>
                <button className={styles.btnApprove} onClick={() => onApprove(mission)}>승인</button>
                <button className={styles.btnReject}  onClick={() => onReject(mission.id)}>거절</button>
              </>
            )}
            {mission.status === 'active' && (
              <>
                <button className={styles.btnApprove} onClick={() => onApprove(mission)}>✅ 승인</button>
                <button
                  className={styles.btnEdit}
                  onClick={() => mission.proposed_by === 'template' ? onEditTemplate(mission) : onEdit()}
                >
                  편집
                </button>
                <button className={styles.btnDelete}  onClick={() => onDelete(mission.id, mission.group_id)}>삭제</button>
              </>
            )}
            {mission.status === 'completed' && (
              <button className={styles.btnUndo} onClick={() => onUndoComplete(mission.id)}>완료 취소</button>
            )}
          </div>
        </div>

        {/* 우측 포인트 영역 */}
        <div className={styles.cardRight}>
          <AppIcon name="coin" size={18} />
          <span className={styles.pointNumber}>{mission.point}</span>
          <span className={styles.pointUnit}>P</span>
        </div>

      </div>
    </div>
  );
}
