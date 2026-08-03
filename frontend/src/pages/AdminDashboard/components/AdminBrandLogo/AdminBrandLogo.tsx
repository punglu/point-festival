import styles from './AdminBrandLogo.module.css';
import MainLogo from '../../../../shared/components/MainLogo';

interface Props {
  size?: 'sm' | 'md';
  showSub?: boolean;
}

const LOGO_PX: Record<'sm' | 'md', number> = { sm: 34, md: 42 };

export default function AdminBrandLogo({ size = 'sm', showSub = false }: Props) {
  return (
    <div className={`${styles.wrap} ${styles[size]}`}>
      <MainLogo variant="wordmark" tone="onDark" size={LOGO_PX[size]} className={styles.logo} />
      <div className={styles.textGroup}>
        <span className={styles.brandText}>몽글</span>
        {showSub && <span className={styles.brandSub}>관리자 패널</span>}
      </div>
    </div>
  );
}
