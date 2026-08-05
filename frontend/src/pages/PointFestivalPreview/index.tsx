import { PointFestivalScreen, pointFestivalFixture } from '../../screens/markpoint/PointFestival';
import styles from './PointFestivalPreview.module.css';

// Presentation-only reproduction of canonical screen 1c (포인트 잔치). The
// content zones now live in screens/markpoint/PointFestival/PointFestivalScreen
// (single-sourced with the real /markpoint product route); this page adds
// only the preview-only dock (DEVICE_CHROME-equivalent, same reasoning as
// the Family Home Preview's own dock — the real route already has
// MongleAppShell's own nav there).

function HomeIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="M4 10.6 12 4.2l8 6.4V19a1.6 1.6 0 0 1-1.6 1.6h-3.2v-5.4H8.8v5.4H5.6A1.6 1.6 0 0 1 4 19z" /></svg>; }
function FestivalIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="M12 21c4.4-4 6.8-7.3 6.8-10.6A6.8 6.8 0 0 0 5.2 10.4C5.2 13.7 7.6 17 12 21z" /><path d="M9.6 9.6h.01M14.4 9.6h.01" /><path d="M9.9 12.6a3 3 0 0 0 4.2 0" /></svg>; }
function ChatIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="M4.4 6.4A2 2 0 0 1 6.4 4.4h11.2a2 2 0 0 1 2 2v7.2a2 2 0 0 1-2 2H9.2l-4.8 3.6z" /><path d="M8.8 10h.01M12 10h.01M15.2 10h.01" /></svg>; }
function PersonIcon() { return <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8.2" r="3.6" /><path d="M5.2 20c1.5-3.9 4-5.8 6.8-5.8s5.3 1.9 6.8 5.8" /></svg>; }

export function PointFestivalPreview() {
  const noOp = () => undefined;
  return (
    <main className={styles.page}>
      <PointFestivalScreen model={pointFestivalFixture} onLogout={noOp} onSelectDay={noOp} onSelectMission={noOp} onHistoryClick={noOp} />
      <nav className={styles.dock} aria-label="미리보기 하단 메뉴">
        <button type="button" onClick={noOp}><HomeIcon /><span>홈</span></button>
        <button type="button" className={styles.activeDock} onClick={noOp}><FestivalIcon /><span>포인트 잔치</span></button>
        <button type="button" onClick={noOp}><ChatIcon /><span>대화</span></button>
        <button type="button" onClick={noOp}><PersonIcon /><span>나</span></button>
      </nav>
    </main>
  );
}
