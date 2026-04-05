import styles from './AdminBrandLogo.module.css';
import clusterLogo from '../../../../assets/logos/brand-icon.png';

interface Props {
  size?: 'sm' | 'md';
  showSub?: boolean;
}

export default function AdminBrandLogo({ size = 'sm', showSub = false }: Props) {
  return (
    <div className={`${styles.wrap} ${styles[size]}`}>
      <img src={clusterLogo} alt="포인트 잔치" className={styles.logo} />
      <div className={styles.textGroup}>
        <span className={styles.brandText}>포인트 잔치</span>
        {showSub && <span className={styles.brandSub}>관리자 패널</span>}
      </div>
    </div>
  );
}
