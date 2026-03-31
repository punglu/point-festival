import { useLocation } from 'react-router-dom';
import styles from './AdminHeader.module.css';
import PlayerFilterBar from '../components/PlayerFilterBar';
import { ADMIN_MENU_ITEMS } from '../constants';

interface Props {
  onMenuToggle: () => void;
}

const TITLE_MAP: Record<string, string> = Object.fromEntries(
  ADMIN_MENU_ITEMS.map((item) => [item.path, item.label])
);

export default function AdminHeader({ onMenuToggle }: Props) {
  const { pathname } = useLocation();
  const title = TITLE_MAP[pathname] ?? '관리자';

  return (
    <header className={styles.header}>
      <button className={styles.menuToggle} onClick={onMenuToggle} aria-label="메뉴">
        ☰
      </button>
      <div className={styles.titleArea}>
        <span className={styles.breadcrumb}>관리자 콘솔 / {title}</span>
        <span className={styles.pageTitle}>{title}</span>
      </div>
      <div className={styles.filterArea}>
        <PlayerFilterBar />
      </div>
    </header>
  );
}
