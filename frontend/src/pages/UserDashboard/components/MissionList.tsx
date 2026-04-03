import styles from '../UserDashboard.module.css';
import { MissionResponse } from '../api/dashboardApi';
import MissionProgressBar from './MissionProgressBar';

interface Props {
  missions: MissionResponse[];
  requestApproval: (missionId: number) => Promise<void>;
}

const STATUS_LABEL: Record<string, string> = {
  failed: '실패',
  rejected: '거절됨',
};

const STATUS_CLASS: Record<string, string> = {
  failed: styles.statusFailed,
  rejected: styles.statusRejected,
};

const POINT_BADGE_CLASS: Record<string, string> = {
  completed: styles.pointBadgeCompleted,
  active: styles.pointBadgeActive,
  pending_approval: styles.pointBadgePending,
};

export default function MissionList({ missions, requestApproval }: Props) {
  return (
    <div className={styles.missionList}>
      {missions.length === 0 && (
        <div className={styles.emptyMsg}>아직 등록된 미션이 없습니다.</div>
      )}
      {missions.map(m => (
        <div
          key={m.id}
          className={`${styles.missionCard} ${m.status === 'failed' ? styles.missionsFailed : ''}`}
        >
          <div className={styles.missionHeader}>
            <span className={m.status === 'completed' ? styles.missionTextCompleted : styles.missionTextActive}>
              {m.text}
            </span>
            <span className={`${styles.pointBadge} ${POINT_BADGE_CLASS[m.status] ?? styles.pointBadgeActive}`}>
              {m.status === 'failed' ? '0P' : `${m.point}P`}
            </span>
          </div>

          {MissionProgressBar({ status: m.status }) !== null ? (
            <MissionProgressBar status={m.status} />
          ) : (
            <span className={`${styles.missionStatus} ${STATUS_CLASS[m.status] ?? ''}`}>
              {STATUS_LABEL[m.status] ?? m.status}
            </span>
          )}

          {m.msg && (
            <div className={`${styles.missionMsg} ${m.sender === '아빠' ? styles.msgDad : styles.msgMom}`}>
              {m.sender && <strong>{m.sender}: </strong>}{m.msg}
            </div>
          )}

          {m.status === 'rejected' && m.rejection_reason && (
            <div className={styles.rejectionReason}>거절 사유: {m.rejection_reason}</div>
          )}

          {m.status === 'active' && (
            <div className={styles.missionAction}>
              <button
                className={styles.actionApprove}
                onClick={() => requestApproval(m.id)}
              >
                완료! 승인 요청
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
