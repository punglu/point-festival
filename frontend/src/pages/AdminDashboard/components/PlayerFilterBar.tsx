import styles from './PlayerFilterBar.module.css';
import { useAdminFilter } from '../hooks/useAdminFilter';

export default function PlayerFilterBar() {
  const { players, selectedPlayerId, selectedDate, setPlayer, setDate, quickDate } = useAdminFilter();

  return (
    <div className={styles.filterBar}>
      <select
        className={styles.playerSelect}
        value={selectedPlayerId ?? ''}
        onChange={(e) => setPlayer(e.target.value ? Number(e.target.value) : null)}
      >
        <option value="">플레이어 선택</option>
        {players.map((p) => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </select>

      <input
        type="date"
        className={styles.datePicker}
        value={selectedDate}
        onChange={(e) => setDate(e.target.value)}
      />

      <div className={styles.quickButtons}>
        <button className={styles.quickBtn} onClick={() => quickDate(-1)}>어제</button>
        <button className={styles.quickBtn} onClick={() => quickDate(0)}>오늘</button>
        <button className={styles.quickBtn} onClick={() => quickDate(1)}>내일</button>
      </div>
    </div>
  );
}
