import styles from './SystemConfig.module.css';

interface Props {
  displayName:    string | null;
  onDisplayName:  (v: string) => void;
}

export default function SystemConfig({ displayName, onDisplayName }: Props) {
  return (
    <div className={styles.section}>
      <div className={styles.sectionTitle}>시스템 설정</div>

      <div className={styles.fieldGroup}>
        <div className={styles.label}>관리자 표시 이름</div>
        <input
          className={styles.input}
          value={displayName ?? ''}
          placeholder="관리자"
          onChange={(e) => onDisplayName(e.target.value)}
        />
      </div>
    </div>
  );
}
