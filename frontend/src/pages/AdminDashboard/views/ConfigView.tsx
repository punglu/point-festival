import styles from './ConfigView.module.css';
import ConfigManager from '../components/ConfigManager';

export default function ConfigView() {
  return (
    <div className={styles.configView}>
      <div className={styles.panel}>
        <ConfigManager />
      </div>
    </div>
  );
}
