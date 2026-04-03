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
    <div className={styles.authView}>
      {/* Indigo 헤더 */}
      <div className={styles.authHeader}>
        <img src="/logo-login.png" alt="포인트 잔치" className={styles.brandLogo} />
        <h1 className={styles.authTitle}>포인트 잔치</h1>
        <p className={styles.authSubtitle}>플레이어를 선택하세요</p>
      </div>

      {/* 플레이어 카드 목록 */}
      <div className={styles.authBody}>
        <div className={styles.playerCardList}>
          {players.map((p, idx) => (
            <PlayerCard
              key={p.id}
              name={p.name}
              photo={p.photo}
              level={thresholds ? calcLevel(p.total_points ?? 0, thresholds) : null}
              isLocked={p.is_locked}
              isAlt={idx % 2 === 1}
              onClick={() => onPlayerSelect({ id: p.id, name: p.name, photo: p.photo })}
            />
          ))}
        </div>
      </div>

      {/* 관리자 로그인 */}
      <div className={styles.authFooter}>
        <button className={styles.adminEntryBtn} onClick={onAdminClick}>
          ⚙️ 관리자 로그인
        </button>
      </div>
    </div>
  );
}
