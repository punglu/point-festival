import { useEffect, useState } from 'react';
import styles from '../Auth.module.css';
import PlayerCard from './PlayerCard';
import { authApi } from '../api/authApi';

function calcLevel(totalPoints: number, thresholds: Record<number, number>): number {
  let level = 1;
  for (const [lv, threshold] of Object.entries(thresholds).sort((a, b) => Number(b[0]) - Number(a[0]))) {
    if (totalPoints >= threshold) { level = Number(lv); break; }
  }
  return level;
}

interface Player {
  id: number;
  name: string;
  photo: string | null;
  total_points: number;
  is_locked: boolean;
  role: string;
}

interface Props {
  onPlayerSelect: (player: { id: number; name: string; photo: string | null }) => void;
  onAdminClick: () => void;
}

export default function PlayerSelectView({ onPlayerSelect, onAdminClick }: Props) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [thresholds, setThresholds] = useState<Record<number, number> | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    authApi.getPlayers(controller.signal)
      .then((list) => {
        if (!controller.signal.aborted) {
          setPlayers(list.filter((p) => p.role === 'player') as Player[]);
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) setPlayers([]);
      });

    fetch('/api/configs/level.thresholds')
      .then(res => res.json())
      .then(data => {
        if (data?.value && !controller.signal.aborted) {
          setThresholds(JSON.parse(data.value));
        }
      })
      .catch(() => {});

    return () => controller.abort();
  }, []);

  return (
    <div className={styles.selectViewWrapper}>
      {/* 선물상자 아이콘 */}
      <div className={styles.giftIcon}>
        <svg width="48" height="48" viewBox="0 0 64 64" fill="none">
          <rect x="10" y="26" width="44" height="28" rx="4" fill="#10b981"/>
          <rect x="10" y="26" width="44" height="8" rx="3" fill="#6ee7b7"/>
          <rect x="29" y="26" width="6" height="28" fill="#ef4444"/>
          <rect x="29" y="26" width="6" height="8" fill="#fca5a5"/>
          <path d="M32 26c-4-8-14-8-14-2s10 2 14 2z" fill="#ef4444"/>
          <path d="M32 26c4-8 14-8 14-2s-10 2-14 2z" fill="#fca5a5"/>
          <rect x="29" y="34" width="6" height="20" rx="1" fill="#dc2626"/>
        </svg>
      </div>

      <h2 className={styles.authTitle}>포인트 잔치</h2>
      <p className={styles.authSubtitle}>플레이어를 선택하세요</p>

      <div className={styles.cardGrid}>
        {players.map((p) => (
          <PlayerCard
            key={p.id}
            name={p.name}
            photo={p.photo}
            level={thresholds ? calcLevel(p.total_points ?? 0, thresholds) : null}
            isLocked={p.is_locked}
            onClick={() => onPlayerSelect({ id: p.id, name: p.name, photo: p.photo })}
          />
        ))}
      </div>

      <button className={styles.adminLinkBtn} onClick={onAdminClick}>
        관리자 로그인
      </button>
    </div>
  );
}
