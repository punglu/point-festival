import { useState } from 'react';
import styles from './DashboardModal.module.css';
import { getLocalToday } from '../../../../../shared/utils/dateUtils';
import { adminApi } from '../../../api/adminApi';
import AdminModal from '../../../components/AdminModal/AdminModal';
import PlayerTab from '../../../components/PlayerTab/PlayerTab';
import { MissionDetailFormScreen } from '../../../../../screens/admin/MissionDetailForm';
import type { MissionDetailFormModel } from '../../../../../screens/admin/MissionDetailForm';
import type { Mission, Player } from '../../../types/admin.types';
import type { CycleInfo } from '../../../hooks/useCycle';

interface Props {
  open:    boolean;
  onClose: () => void;
  missions: Mission[];
  players:  Player[];
  cycle:    Pick<CycleInfo, 'startDate' | 'endDate'>;
  onChanged?: () => void;
}

const STATUS_LABEL: Record<string, string> = {
  active: '진행중', completed: '완료', pending_approval: '승인대기',
  failed: '실패', rejected: '거절', proposed: '제안',
};
const STATUS_COLOR: Record<string, string> = {
  active: '#059669', completed: '#4338CA', pending_approval: '#D97706',
  failed: '#DC2626', rejected: '#DC2626', proposed: '#6366F1',
};

// canonical 2m (미션 상세 폼) 실데이터 adapter. 프로젝트 Mission에는 다건
// 승인/반려 이력 API가 없다 (TRUE_FUNCTIONAL_GAP, 신규 API 없이 억지로 만들지
// 않음) -- 이 미션 행 자신이 실제로 겪은 상태 1건만 history에 매핑한다.
function toMissionDetailFormModel(mission: Mission, player: Player | undefined): MissionDetailFormModel {
  const history: MissionDetailFormModel['history'] =
    mission.status === 'completed' || mission.status === 'rejected'
      ? [{
          name: player?.name ?? '?',
          time: mission.updated_at,
          status: mission.status === 'completed' ? '승인' : '반려',
        }]
      : [];
  return {
    title: mission.text,
    description: mission.proposal_reason ?? mission.rejection_reason ?? '',
    assignees: player?.name ?? '?',
    points: mission.point,
    history,
  };
}

export default function ActiveMissionDetailModal({ open, onClose, missions, players, cycle, onChanged }: Props) {
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
  const [detailMissionId, setDetailMissionId] = useState<number | null>(null);
  const today = getLocalToday();

  const filtered = missions.filter((m) =>
    m.status === 'active' &&
    m.date >= cycle.startDate &&
    m.date >= today &&
    (selectedPlayer === null || m.player_id === selectedPlayer)
  );

  // date 기준 내림차순 그룹핑
  const grouped: Record<string, Mission[]> = {};
  filtered.forEach((m) => {
    if (!grouped[m.date]) grouped[m.date] = [];
    grouped[m.date].push(m);
  });
  const sortedDates = Object.keys(grouped).sort((a, b) => a.localeCompare(b));

  const detailMission = detailMissionId !== null ? missions.find((m) => m.id === detailMissionId) ?? null : null;
  const detailPlayer = detailMission ? players.find((p) => p.id === detailMission.player_id) : undefined;

  const handleDelete = async () => {
    if (!detailMission) return;
    try {
      await adminApi.deleteMission(detailMission.id);
      setDetailMissionId(null);
      onChanged?.();
    } catch { /* ignore -- surfaced via existing admin toast conventions elsewhere */ }
  };

  return (
    <AdminModal open={open} onClose={onClose} title="활성 미션 상세" width={520}>
      <PlayerTab players={players} selected={selectedPlayer} onSelect={setSelectedPlayer} />
      <div className={styles.listBody}>
        {sortedDates.length === 0 ? (
          <div className={styles.empty}>활성 미션이 없습니다</div>
        ) : (
          sortedDates.map((date) => (
            <div key={date}>
              <div className={styles.dateHeader}>{date}</div>
              {grouped[date].map((m) => {
                const player = players.find((p) => p.id === m.player_id);
                return (
                  <button
                    type="button"
                    key={m.id}
                    className={`${styles.missionRow} ${styles.missionRowButton}`}
                    onClick={() => setDetailMissionId(m.id)}
                  >
                    <span className={styles.missionText}>{m.text}</span>
                    <span className={styles.playerBadge}>{player?.name ?? '?'}</span>
                    <span className={styles.pointBadge}>{m.point}pt</span>
                    <span
                      className={styles.statusBadge}
                      style={{ color: STATUS_COLOR[m.status] }}
                    >
                      {STATUS_LABEL[m.status] ?? m.status}
                    </span>
                  </button>
                );
              })}
            </div>
          ))
        )}
      </div>

      {detailMission && (
        <div className={styles.detailOverlay} data-testid="admin-mission-detail-overlay">
          <MissionDetailFormScreen
            embedded
            model={toMissionDetailFormModel(detailMission, detailPlayer)}
            onClose={() => setDetailMissionId(null)}
            onSave={() => setDetailMissionId(null)}
            onDelete={() => void handleDelete()}
          />
        </div>
      )}
    </AdminModal>
  );
}
