import styles from './MissionProgressBar.module.css';

interface Props {
  status: string;
}

const STEPS = [
  {
    key:   'active',
    label: '도전중',
    icon: (
      <svg width="9" height="9" viewBox="0 0 10 10" fill="none">
        <polygon points="2,1 9,5 2,9" fill="currentColor" />
      </svg>
    ),
  },
  {
    key:   'pending_approval',
    label: '확인중',
    icon: (
      <svg width="9" height="9" viewBox="0 0 12 12" fill="none">
        <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.5" />
        <path d="M6 3.5V6.2L7.8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    key:   'completed',
    label: '완료!',
    icon: (
      <svg width="9" height="9" viewBox="0 0 10 10" fill="none">
        <path d="M1.5 5L4 7.5L8.5 2.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
];

const STEP_THEME = {
  active:           { node: styles.nodeActive,   line: styles.lineFilled },
  pending_approval: { node: styles.nodePending,  line: styles.lineFilled },
  completed:        { node: styles.nodeCompleted, line: styles.lineFilled },
};

export default function MissionProgressBar({ status }: Props) {
  const currentIndex = STEPS.findIndex(s => s.key === status);
  if (currentIndex < 0) return null;

  return (
    <div className={styles.bar}>
      {STEPS.map((step, i) => {
        const isPast    = i < currentIndex;
        const isCurrent = i === currentIndex;
        const theme     = STEP_THEME[status as keyof typeof STEP_THEME];

        let nodeClass = styles.nodeFuture;
        if (isCurrent) nodeClass = theme?.node ?? styles.nodeActive;
        else if (isPast) nodeClass = styles.nodePast;

        return (
          <div key={step.key} className={styles.stepGroup}>
            {/* 왼쪽 연결선 (첫 노드 제외) */}
            {i > 0 && (
              <div className={`${styles.line} ${isPast || isCurrent ? theme?.line ?? styles.lineFilled : styles.lineEmpty}`} />
            )}

            <div className={styles.stepWrap}>
              <div className={`${styles.node} ${nodeClass} ${isCurrent ? styles.nodeCurrent : ''}`}>
                {step.icon}
              </div>
              <span className={`${styles.label} ${isCurrent ? styles.labelCurrent : isPast ? styles.labelPast : styles.labelFuture}`}>
                {step.label}
              </span>
            </div>

            {/* 오른쪽 연결선 (마지막 노드 제외) */}
            {i < STEPS.length - 1 && (
              <div className={`${styles.line} ${isPast ? theme?.line ?? styles.lineFilled : styles.lineEmpty}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
