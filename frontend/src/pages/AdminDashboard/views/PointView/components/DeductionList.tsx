import { useState } from 'react';
import styles from './DeductionList.module.css';
import type { Deduction, Player } from '../../../types/admin.types';

type SortKey = 'date' | 'player' | 'amount';
type SortDir = 'asc' | 'desc';

interface Props {
  deductions: Deduction[];
  players:    Player[];
  onEdit:     (d: Deduction) => void;
  onDelete:   (id: number) => void;
}

export default function DeductionList({ deductions, players, onEdit, onDelete }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>('date');
  const [sortDir, setSortDir] = useState<SortDir>('desc');

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  const sorted = [...deductions].sort((a, b) => {
    let cmp = 0;
    if (sortKey === 'date') {
      cmp = a.date.localeCompare(b.date);
    } else if (sortKey === 'player') {
      const pa = players.find((p) => p.id === a.player_id)?.name ?? '';
      const pb = players.find((p) => p.id === b.player_id)?.name ?? '';
      cmp = pa.localeCompare(pb);
    } else if (sortKey === 'amount') {
      cmp = a.amount - b.amount;
    }
    return sortDir === 'asc' ? cmp : -cmp;
  });

  const arrow = (key: SortKey) =>
    sortKey === key ? (sortDir === 'asc' ? ' ↑' : ' ↓') : '';

  return (
    <div className={styles.section}>
      <div className={styles.sectionHeader}>
        <span className={styles.sectionTitle}>차감 내역</span>
        <span className={styles.count}>{deductions.length}건</span>
      </div>
      {deductions.length === 0 ? (
        <div className={styles.empty}>차감 내역이 없습니다</div>
      ) : (
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th} onClick={() => toggleSort('date')}>날짜{arrow('date')}</th>
              <th className={styles.th}>사유</th>
              <th className={styles.th} onClick={() => toggleSort('player')}>플레이어{arrow('player')}</th>
              <th className={`${styles.th} ${styles.thRight}`} onClick={() => toggleSort('amount')}>차감{arrow('amount')}</th>
              <th className={styles.th} />
            </tr>
          </thead>
          <tbody>
            {sorted.map((d) => {
              const player = players.find((p) => p.id === d.player_id);
              return (
                <tr key={d.id} className={styles.row}>
                  <td className={styles.td}>{d.date}</td>
                  <td className={`${styles.td} ${styles.reason}`}>{d.reason}</td>
                  <td className={styles.td}>
                    {player && <span className={styles.playerBadge}>{player.name}</span>}
                  </td>
                  <td className={`${styles.td} ${styles.amount}`}>-{d.amount}pt</td>
                  <td className={styles.td}>
                    <div className={styles.actions}>
                      <button className={styles.btnEdit}   onClick={() => onEdit(d)}>수정</button>
                      <button className={styles.btnDelete} onClick={() => onDelete(d.id)}>삭제</button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
