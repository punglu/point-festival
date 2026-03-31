import styles from './MobileDrawer.module.css';
import Sidebar from './Sidebar';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function MobileDrawer({ isOpen, onClose }: Props) {
  return (
    <>
      <div
        className={`${styles.overlay} ${isOpen ? styles.overlayOpen : ''}`}
        onClick={onClose}
      />
      <div className={`${styles.drawer} ${isOpen ? styles.drawerOpen : ''}`}>
        <Sidebar onNavigate={onClose} />
      </div>
    </>
  );
}
