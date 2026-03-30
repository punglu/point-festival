import React from 'react';
import styles from '../UserDashboard.module.css';

interface MissionProgressBarProps {
  status: string;
}

const STEPS = [
  { key: 'active', label: '도전중' },
  { key: 'pending_approval', label: '확인중' },
  { key: 'completed', label: '완료!' },
];

export default function MissionProgressBar({ status }: MissionProgressBarProps) {
  const currentIndex = STEPS.findIndex(s => s.key === status);
  // rejected, failed, proposed 등은 바를 표시하지 않음
  if (currentIndex < 0) return null;

  return (
    <div className={styles.missionProgressBar}>
      {STEPS.map((step, i) => (
        <React.Fragment key={step.key}>
          <div
            className={`${styles.progressStep} ${i <= currentIndex ? styles.progressStepActive : ''}`}
          >
            <div className={styles.progressDot} />
            <span className={styles.progressLabel}>{step.label}</span>
          </div>
          {i < STEPS.length - 1 && (
            <div
              className={`${styles.progressLine} ${i < currentIndex ? styles.progressLineActive : ''}`}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
