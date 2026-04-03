import styles from './ProposedMissionSection.module.css';
import type { Mission, Player } from '../../../types/admin.types';

interface Props {
  missions:  Mission[];
  players:   Player[];
  onApprove: (m: Mission) => void;
  onReject:  (id: number) => void;
}

export default function ProposedMissionSection({ missions, players, onApprove, onReject }: Props) {
  return (
    <div className={styles.section}>
      <div className={styles.sectionHeader}>
        <span className={styles.sectionTitle}>✋ 아이 제안 미션</span>
        <span className={styles.countBadge}>{missions.length}건</span>
      </div>
      <div className={styles.grid}>
        {missions.map((m) => {
          const player = players.find((p) => p.id === m.player_id);
          return (
            <div key={m.id} className={styles.card}>
              <div className={styles.missionText}>{m.text}</div>
              <div className={styles.metaRow}>
                {player && <span className={styles.playerBadge}>{player.name}</span>}
                <span className={styles.pointBadge}>{m.point}pt</span>
              </div>
              {m.proposal_reason && (
                <div className={styles.reason}>💬 {m.proposal_reason}</div>
              )}
              <div className={styles.actions}>
                <button className={styles.btnApprove} onClick={() => onApprove(m)}>승인</button>
                <button className={styles.btnReject}  onClick={() => onReject(m.id)}>거절</button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
