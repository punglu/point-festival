import styles from '../AdminDashboard.module.css';
import { AdminTab } from '../hooks/useAdmin';

interface Props {
  activeTab: AdminTab;
  setActiveTab: (tab: AdminTab) => void;
}

const TABS: { key: AdminTab; label: string }[] = [
  { key: 'missions', label: '미션' },
  { key: 'points', label: '포인트' },
  { key: 'cheer', label: '응원' },
  { key: 'players', label: '플레이어' },
  { key: 'more', label: '더보기' },
];

export default function AdminNav({ activeTab, setActiveTab }: Props) {
  return (
    <nav className={styles.adminNav}>
      {TABS.map((tab) => (
        <button
          key={tab.key}
          className={`${styles.adminNavTab} ${activeTab === tab.key ? styles.adminNavTabActive : ''}`}
          onClick={() => setActiveTab(tab.key)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
