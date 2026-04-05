import styles from './MissionList.module.css';
import { MissionResponse } from '../api/dashboardApi';

function formatTime(createdAt: string | null | undefined): string | null {
  if (!createdAt) return null;
  try {
    const d = new Date(createdAt);
    const h = d.getHours();
    const m = String(d.getMinutes()).padStart(2, '0');
    return h < 12 ? `오전 ${h || 12}:${m}` : `오후 ${h - 12 || 12}:${m}`;
  } catch { return null; }
}

interface Props {
  missions: MissionResponse[];
  requestApproval: (missionId: number) => Promise<void>;
}

const PROGRESS_STATUSES = ['active', 'pending_approval', 'completed'];

export default function MissionList({ missions, requestApproval }: Props) {
  return (
    <div className={styles.missionList}>
      {missions.length === 0 && (
        <div className={styles.emptyMsg}>아직 등록된 미션이 없습니다.</div>
      )}
      {missions.map(mission => (
        <div
          key={mission.id}
          className={[
            styles.card,
            mission.status === 'completed' ? styles.cardCompleted : '',
            mission.status === 'failed'    ? styles.cardFailed    : '',
          ].join(' ')}
        >
          {/* 좌측 영역 */}
          <div className={styles.cardLeft}>
            {/* Row 1: 미션명 + 상태 뱃지 */}
            <div className={styles.cardRow1}>
              <span className={`${styles.missionName} ${mission.status === 'failed' ? styles.nameStrike : ''}`}>
                {mission.text}
              </span>
              <span className={`${styles.statusBadge} ${styles[`badge_${mission.status}` as keyof typeof styles] ?? ''}`}>
                {mission.status === 'active'           && '진행중'}
                {mission.status === 'pending_approval' && '승인 대기'}
                {mission.status === 'completed'        && '완료'}
                {mission.status === 'failed'           && '실패'}
                {mission.status === 'proposed'         && '제안'}
                {mission.status === 'rejected'         && '거절'}
              </span>
            </div>

            {/* Row 2: 출제자 + 시간 */}
            {(mission.sender || mission.created_at) && (
              <div className={styles.cardMeta}>
                {mission.sender && <span>{mission.sender}</span>}
                {mission.sender && mission.created_at && <span> · </span>}
                {mission.created_at && <span>{formatTime(mission.created_at)}</span>}
              </div>
            )}

            {/* Row 3: 미니 도트 프로그레스 */}
            {PROGRESS_STATUSES.includes(mission.status) && (
              <div className={styles.progressRow}>
                <div className={styles.progressDot}>
                  <span className={`${styles.dot} ${styles.dotFilled} ${mission.status === 'completed' ? styles.dotGreen : styles.dotPurple}`} />
                  <span className={`${styles.dotLabel} ${styles.dotLabelActive}`}>도전</span>
                </div>
                <div className={`${styles.progressLine} ${['pending_approval', 'completed'].includes(mission.status) ? styles.lineFilled : ''}`} />
                <div className={styles.progressDot}>
                  <span className={`${styles.dot} ${['pending_approval', 'completed'].includes(mission.status) ? styles.dotFilled : ''} ${mission.status === 'completed' ? styles.dotGreen : mission.status === 'pending_approval' ? styles.dotAmber : ''}`} />
                  <span className={`${styles.dotLabel} ${['pending_approval', 'completed'].includes(mission.status) ? styles.dotLabelActive : ''}`}>확인</span>
                </div>
                <div className={`${styles.progressLine} ${mission.status === 'completed' ? `${styles.lineFilled} ${styles.lineGreen}` : ''}`} />
                <div className={styles.progressDot}>
                  <span className={`${styles.dot} ${mission.status === 'completed' ? `${styles.dotFilled} ${styles.dotGreen}` : ''}`} />
                  <span className={`${styles.dotLabel} ${mission.status === 'completed' ? styles.dotLabelActive : ''}`}>완료</span>
                </div>
              </div>
            )}

            {/* Row 4: 액션 버튼 (active만) */}
            {mission.status === 'active' && (
              <button className={styles.actionBtn} onClick={() => requestApproval(mission.id)}>
                완료! 승인 요청
              </button>
            )}

            {/* pending 상태 메시지 */}
            {mission.status === 'pending_approval' && (
              <div className={styles.pendingMsg}>부모님 확인 중...</div>
            )}
          </div>

          {/* 우측: 포인트 영역 */}
          <div className={styles.pointArea}>
            {mission.status === 'completed' ? (
              <>
                <div className={`${styles.pointCircle} ${styles.pointCircleGreen}`}>✅</div>
                <span className={`${styles.pointValue} ${styles.pointGreen}`}>{mission.point}P</span>
              </>
            ) : mission.status === 'failed' ? (
              <span className={`${styles.pointValue} ${styles.pointStrike}`}>{mission.point}P</span>
            ) : (
              <>
                <div className={`${styles.pointCircle} ${styles.pointCircleAmber}`}>💰</div>
                <span className={`${styles.pointValue} ${styles.pointAmber}`}>{mission.point}P</span>
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
