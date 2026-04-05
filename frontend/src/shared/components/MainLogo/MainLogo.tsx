import styles from './MainLogo.module.css';
import clusterSrc from '../../../assets/logos/auth-logo.png';

interface MainLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

export default function MainLogo({ size = 'md', showText = true }: MainLogoProps) {
  return (
    <div className={`${styles.logo} ${styles[size]}`}>
      <img src={clusterSrc} alt="포인트 잔치" className={styles.cluster} />
      {showText && <span className={styles.title}>포인트 잔치</span>}
    </div>
  );
}
