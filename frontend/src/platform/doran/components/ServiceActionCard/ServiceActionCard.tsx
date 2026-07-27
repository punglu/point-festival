import { Card } from '../../../../shared/components/Card';
import styles from './ServiceActionCard.module.css';

export interface ServiceActionCardProps {
  serviceLabel: string;
  title: string;
  description?: string;
  timestamp: string;
  pointLabel?: string;
  actionLabel?: string;
  onAction?: () => void;
}

/**
 * 서비스 이벤트 요약 카드. raw JSON을 표시하지 않고, 일반 대화 bubble과
 * 구분되는 read-only 카드 표현만 제공한다. onAction은 소비처가 정의하는
 * 콜백일 뿐, 이 component는 Mark Point 업무 상태를 직접 변경하지 않는다.
 */
export default function ServiceActionCard({
  serviceLabel,
  title,
  description,
  timestamp,
  pointLabel,
  actionLabel,
  onAction,
}: ServiceActionCardProps) {
  return (
    <Card variant="section" className={styles.card} aria-label={`${serviceLabel} 서비스 알림`}>
      <div className={styles.meta}>
        <span className={styles.serviceLabel}>{serviceLabel}</span>
        <span className={styles.timestamp}>{timestamp}</span>
      </div>
      <div className={styles.titleRow}>
        <strong className={styles.title}>{title}</strong>
        {pointLabel && <span className={styles.pointLabel}>{pointLabel}</span>}
      </div>
      {description && <p className={styles.description}>{description}</p>}
      {actionLabel && onAction && (
        <button type="button" className={styles.actionButton} onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </Card>
  );
}
