import styles from '../UserDashboard.module.css';
import { MissionResponse, DeductionResponse, DailyPointResponse } from '../api/dashboardApi';

type StatType = 'earned' | 'balance' | 'pending';

interface Props {
  type: StatType | null;
  isOpen: boolean;
  onClose: () => void;
  missions: MissionResponse[];
  deductions?: DeductionResponse[];
  dailyPoint: DailyPointResponse | null;
}

const TYPE_LABEL: Record<StatType, string> = {
  earned: '오늘 획득 포인트',
  balance: '현재 보유 포인트',
  pending: '남은 미션 포인트',
};

export default function StatDetailModal({ type, isOpen, onClose, missions, dailyPoint }: Props) {
  if (!isOpen || !type) return null;

  const completedMissions = missions.filter(m => m.status === 'completed');
  const activeMissions = missions.filter(m => m.status === 'active');

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalBox} onClick={e => e.stopPropagation()}>
        <div className={styles.modalTitle}>{TYPE_LABEL[type]}</div>

        {type === 'earned' && (
          <div className={styles.statModalList}>
            {completedMissions.length === 0 ? (
              <div className={styles.emptyMsg}>완료된 미션이 없습니다.</div>
            ) : (
              completedMissions.map(m => (
                <div key={m.id} className={styles.statModalRow}>
                  <span>{m.text}</span>
                  <span className={styles.statModalEarned}>+{m.point}P</span>
                </div>
              ))
            )}
            <div className={styles.statModalTotal}>
              <span>합계</span>
              <span className={styles.statModalEarnedLight}>{dailyPoint?.earned ?? 0}P</span>
            </div>
          </div>
        )}

        {type === 'balance' && (
          <div className={styles.statModalSection}>
            <div className={styles.statModalRowGap}>
              <span>오늘 획득</span>
              <span className={styles.statModalEarnedLight}>+{dailyPoint?.earned ?? 0}P</span>
            </div>
            <div className={styles.statModalRowGap}>
              <span>오늘 사용</span>
              <span className={styles.statModalSpent}>-{dailyPoint?.spent ?? 0}P</span>
            </div>
            <div className={styles.statModalTotal}>
              <span>잔액</span>
              <span className={styles.statModalBalance}>{dailyPoint?.balance ?? 0}P</span>
            </div>
          </div>
        )}

        {type === 'pending' && (
          <div className={styles.statModalList}>
            {activeMissions.length === 0 ? (
              <div className={styles.emptyMsg}>진행 중인 미션이 없습니다.</div>
            ) : (
              activeMissions.map(m => (
                <div key={m.id} className={styles.statModalRow}>
                  <span>{m.text}</span>
                  <span className={styles.statModalPending}>{m.point}P</span>
                </div>
              ))
            )}
          </div>
        )}

        <button className={styles.modalClose} onClick={onClose}>닫기</button>
      </div>
    </div>
  );
}
