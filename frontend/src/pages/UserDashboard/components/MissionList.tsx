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

export default function MissionList({ missions, requestApproval }: Props) {
  if (missions.length === 0) {
    return <div className={styles.emptyMsg}>오늘의 미션이 없습니다.</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {missions.map(m => (
        <div
          key={m.id}
          className={`${styles.missionCard} ${m.status === 'failed' ? styles.missionsFailed : ''}`}
        >
          <div className={styles.missionHeader}>
            <span className={styles.missionTitle}>{m.text}</span>
            {m.status === 'failed' ? (
              <span className={styles.pointValue}>
                <span className={styles.coinIcon}>P</span>0
              </span>
            ) : (
              <span className={styles.pointValue}>
                <span className={styles.coinIcon}>P</span>{m.point}
              </span>
            )}
          </div>

          {/* active / pending_approval / completed → 진행 바 표시 */}
          {MissionProgressBar({ status: m.status }) !== null ? (
            <MissionProgressBar status={m.status} />
          ) : (
            // failed / rejected → 텍스트 배지 폴백
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
