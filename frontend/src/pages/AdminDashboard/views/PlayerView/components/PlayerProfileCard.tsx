import styles from './PlayerProfileCard.module.css';
import { PLAYER_COLORS } from '../../../constants/admin.constants';
import type { Player } from '../../../types/admin.types';

interface Props {
  player:                       Player;
  index:                        number;
  achievementRate:              number;
  totalMissions:                number;
  onChangePin:                  () => void;
  onChangePhoto:                () => void;
  onToggleLock:                 () => void;
  onToggleDashboardVisibility:  () => void;
  onDelete:                     () => void;
}

export default function PlayerProfileCard({
  player, index, achievementRate, totalMissions,
  onChangePin, onChangePhoto, onToggleLock,
  onToggleDashboardVisibility, onDelete,
}: Props) {
  const color = PLAYER_COLORS[index % PLAYER_COLORS.length];

  return (
    <div className={styles.card}>
      <div className={styles.top}>
        {player.photo ? (
          <img src={player.photo} alt={player.name} className={styles.avatar} />
        ) : (
          <div className={styles.avatarFallback} style={{ background: color }}>
            {player.name.charAt(0)}
          </div>
        )}
        <div className={styles.info}>
          <div className={styles.name}>{player.name}</div>
          {player.status_msg && <div className={styles.statusMsg}>{player.status_msg}</div>}
          {player.is_locked && <div className={styles.lockedBadge}>잠금됨</div>}
          {!player.is_dashboard_visible && <div className={styles.hiddenBadge}>대시보드 숨김</div>}
        </div>
      </div>

      <div className={styles.stats}>
        <div className={styles.stat}>
          <div className={styles.statValue}>{totalMissions}개</div>
          <div className={styles.statLabel}>전체 미션</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>{achievementRate}%</div>
          <div className={styles.statLabel}>달성률</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>{player.last_login ? new Date(player.last_login).toLocaleDateString('ko-KR') : '-'}</div>
          <div className={styles.statLabel}>마지막 로그인</div>
        </div>
      </div>

      <div className={styles.actions}>
        <button className={styles.btnAction} onClick={onChangePin}>PIN 변경</button>
        <button className={styles.btnAction} onClick={onChangePhoto}>사진 변경</button>
        <button className={player.is_locked ? styles.btnDanger : styles.btnAction} onClick={onToggleLock}>
          {player.is_locked ? '잠금 해제' : '잠금'}
        </button>
        <button className={player.is_dashboard_visible ? styles.btnAction : styles.btnWarning} onClick={onToggleDashboardVisibility}>
          {player.is_dashboard_visible ? '대시보드 숨김' : '대시보드 노출'}
        </button>
        <button className={styles.btnDelete} onClick={onDelete}>삭제</button>
      </div>
    </div>
  );
}
