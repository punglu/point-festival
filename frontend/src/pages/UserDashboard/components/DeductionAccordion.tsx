import styles from '../UserDashboard.module.css';
import { DeductionResponse } from '../api/dashboardApi';

interface Props {
  deductions: DeductionResponse[];
  totalDeducted: number;
  isOpen: boolean;
  onToggle: () => void;
}

export default function DeductionAccordion({ deductions, totalDeducted, isOpen, onToggle }: Props) {
  return (
    <div className={styles.deductSection}>
      <div className={styles.deductHeader} onClick={onToggle}>
        <span className={styles.deductHeaderTitle}>📉 포인트 사용 내역</span>
        <div className={styles.deductHeaderRight}>
          {totalDeducted > 0 && (
            <span className={styles.deductTotal}>-{totalDeducted}P</span>
          )}
          <span className={`${styles.deductChevron} ${isOpen ? styles.deductChevronOpen : ''}`}>
            ▼
          </span>
        </div>
      </div>

      {isOpen && (
        <div className={styles.deductList}>
          {deductions.length === 0 ? (
            <div className={styles.deductEmpty}>사용 내역이 없습니다.</div>
          ) : (
            deductions.map(d => (
              <div key={d.id} className={styles.deductItem}>
                <span>{d.reason}</span>
                <span className={styles.deductAmount}>-{d.amount}P</span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
