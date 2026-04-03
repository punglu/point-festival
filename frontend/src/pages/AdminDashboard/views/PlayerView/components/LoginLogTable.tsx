import { useState, useMemo } from 'react';
import styles from './LoginLogTable.module.css';
import type { LoginLog, Player } from '../../../types/admin.types';

interface Props {
  logs:    LoginLog[];
  players: Player[];
}

export default function LoginLogTable({ logs, players }: Props) {
  const [filterPlayer, setFilterPlayer] = useState<number | null>(null);
  const [dateFrom,     setDateFrom]     = useState('');
  const [dateTo,       setDateTo]       = useState('');

  const filtered = useMemo(() => {
    return logs.filter((log) => {
      if (filterPlayer !== null && log.player_id !== filterPlayer) return false;
      const logDate = log.created_at.slice(0, 10);
      if (dateFrom && logDate < dateFrom) return false;
      if (dateTo   && logDate > dateTo)   return false;
      return true;
    });
  }, [logs, filterPlayer, dateFrom, dateTo]);

  return (
    <div className={styles.section}>
      <div className={styles.header}>
        <span>최근 로그인 기록</span>
        <div className={styles.filters}>
          <div className={styles.playerTabs}>
            <button
              className={filterPlayer === null ? styles.tabActive : styles.tab}
              onClick={() => setFilterPlayer(null)}
            >
              전체
            </button>
            {players.map((p) => (
              <button
                key={p.id}
                className={filterPlayer === p.id ? styles.tabActive : styles.tab}
                onClick={() => setFilterPlayer(p.id)}
              >
                {p.name}
              </button>
            ))}
          </div>
          <div className={styles.dateRange}>
            <input
              type="date"
              className={styles.dateInput}
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
            <span className={styles.dateSep}>~</span>
            <input
              type="date"
              className={styles.dateInput}
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </div>
        </div>
      </div>
      {filtered.length === 0 ? (
        <div className={styles.empty}>로그인 기록이 없습니다</div>
      ) : (
        filtered.map((log) => {
          const player = players.find((p) => p.id === log.player_id);
          return (
            <div key={log.id} className={styles.row}>
              <div className={log.success ? styles.dotSuccess : styles.dotFail} />
              <span className={styles.playerName}>{player?.name ?? `#${log.player_id}`}</span>
              <span className={log.success ? styles.badgeSuccess : styles.badgeFail}>
                {log.success ? '성공' : '실패'}
              </span>
              <span className={styles.date}>{new Date(log.created_at).toLocaleString('ko')}</span>
            </div>
          );
        })
      )}
    </div>
  );
}
