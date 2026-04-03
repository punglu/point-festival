import styles from './PlayerTab.module.css';

interface PlayerTabProps {
  players: { id: number; name: string }[];
  selected: number | null;
  onSelect: (playerId: number | null) => void;
}

export default function PlayerTab({ players, selected, onSelect }: PlayerTabProps) {
  return (
    <div className={styles.tabGroup}>
      <button
        className={selected === null ? styles.tabActive : styles.tab}
        onClick={() => onSelect(null)}
      >
        전체
      </button>
      {players.map((p) => (
        <button
          key={p.id}
          className={selected === p.id ? styles.tabActive : styles.tab}
          onClick={() => onSelect(p.id)}
        >
          {p.name}
        </button>
      ))}
    </div>
  );
}
