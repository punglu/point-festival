import styles from '../Auth.module.css';

interface Player {
  id: number;
  name: string;
  isLocked: boolean;
}

interface Props {
  players: Player[];
  onSelect: (playerId: number) => void;
}

export default function PlayerSelector({ players, onSelect }: Props) {
  if (!players.length) {
    return (
      <div className={styles.playerSelector}>
        <div className={styles.emptyState}>등록된 아이가 없습니다.</div>
      </div>
    );
  }

  return (
    <div className={styles.playerSelector}>
      <h3 className={styles.playerSelectorTitle}>👦 누구의 미션을 볼까요?</h3>
      <div className={styles.playerButtons}>
        {players.map((p) => (
          <button
            key={p.id}
            className={styles.playerBtn}
            onClick={() => onSelect(p.id)}
          >
            {p.name} {p.isLocked ? '🔒' : ''}
          </button>
        ))}
      </div>
    </div>
  );
}
