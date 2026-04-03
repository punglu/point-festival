import { useState } from 'react';
import styles from './MissionView.module.css';
import { useMissionView } from './hooks/useMissionView';
import MissionCard from './components/MissionCard';
import MissionCardEdit from './components/MissionCardEdit';
import ProposedMissionSection from './components/ProposedMissionSection';
import NewMissionModal from './components/NewMissionModal';
import BatchCopyModal from './components/BatchCopyModal';
import type { Mission } from '../../types/admin.types';

export default function MissionView() {
  const {
    players, selectedPlayer, setSelectedPlayer,
    selectedDate, setSelectedDate,
    proposedMissions, regularMissions, loading,
    approve, reject, deleteMission, updateMission, undoComplete, createMission,
    reload,
  } = useMissionView();

  const [showNew,     setShowNew]     = useState(false);
  const [showBatch,   setShowBatch]   = useState(false);
  const [editingId,   setEditingId]   = useState<number | null>(null);

  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <h1 className={styles.title}>미션 관리</h1>
        <div className={styles.headerActions}>
          <button className={styles.btnSecondary} onClick={() => setShowBatch(true)}>과거 미션 가져오기</button>
          <button className={styles.btnPrimary}   onClick={() => setShowNew(true)}>+ 미션 추가</button>
        </div>
      </div>

      <div className={styles.filters}>
        <span className={styles.filterLabel}>플레이어</span>
        <div className={styles.playerTabs}>
          <button
            className={selectedPlayer === null ? styles.playerTabActive : styles.playerTab}
            onClick={() => setSelectedPlayer(null)}
          >
            전체
          </button>
          {players.map((p) => (
            <button
              key={p.id}
              className={selectedPlayer === p.id ? styles.playerTabActive : styles.playerTab}
              onClick={() => setSelectedPlayer(p.id)}
            >
              {p.name}
            </button>
          ))}
        </div>
        <input
          type="date"
          className={styles.datePicker}
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />
      </div>

      {proposedMissions.length > 0 && (
        <div className={styles.sectionGap}>
          <ProposedMissionSection
            missions={proposedMissions}
            players={players}
            onApprove={approve}
            onReject={(id) => reject(id)}
          />
        </div>
      )}

      {loading ? (
        <div className={styles.loading}>로딩 중...</div>
      ) : regularMissions.length === 0 ? (
        <div className={styles.empty}>이 날짜에 미션이 없습니다</div>
      ) : (
        <div className={styles.grid}>
          {regularMissions.map((m: Mission) =>
            editingId === m.id ? (
              <MissionCardEdit
                key={m.id}
                mission={m}
                onSave={(data) => { updateMission(m.id, data); setEditingId(null); }}
                onCancel={() => setEditingId(null)}
              />
            ) : (
              <MissionCard
                key={m.id}
                mission={m}
                players={players}
                onApprove={approve}
                onReject={(id) => reject(id)}
                onDelete={deleteMission}
                onEdit={() => setEditingId(m.id)}
                onUndoComplete={undoComplete}
              />
            )
          )}
        </div>
      )}

      <NewMissionModal
        open={showNew}
        onClose={() => setShowNew(false)}
        players={players}
        defaultDate={selectedDate}
        onCreate={createMission}
      />

      <BatchCopyModal
        open={showBatch}
        onClose={() => setShowBatch(false)}
        players={players}
        onDone={reload}
      />
    </div>
  );
}
