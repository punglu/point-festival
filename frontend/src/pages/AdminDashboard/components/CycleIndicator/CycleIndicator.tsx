import styles from './CycleIndicator.module.css';
import type { CycleInfo } from '../../hooks/useCycle';

interface CycleIndicatorProps {
  cycle: Pick<CycleInfo, 'displayStart' | 'displayEnd'>;
}

export default function CycleIndicator({ cycle }: CycleIndicatorProps) {
  return (
    <span className={styles.badge}>
      <span className={styles.dot} />
      이번 주기 ({cycle.displayStart} ~ {cycle.displayEnd})
    </span>
  );
}
