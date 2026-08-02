import { useState } from 'react';
import styles from './PointView.module.css';
import { usePointView } from './hooks/usePointView';
import PlayerPointSummary from './components/PlayerPointSummary';
import DeductionList from './components/DeductionList';
import AddDeductionModal from './components/AddDeductionModal';
import EditDeductionModal from './components/EditDeductionModal';
import type { Deduction } from '../../types/admin.types';
import { PointPolicyEditorScreen, pointPolicyEditorFixture } from '../../../../screens/admin/PointPolicyEditor';

export default function PointView() {
  const {
    players, selectedPlayer, setSelectedPlayer,
    selectedDate, setSelectedDate,
    deductions, dailyPoints, loading,
    addDeduction, updateDeduction, deleteDeduction,
  } = usePointView();

  const [showAdd,      setShowAdd]      = useState(false);
  const [editTarget,   setEditTarget]   = useState<Deduction | null>(null);
  const [showPolicy,   setShowPolicy]   = useState(false);

  const visiblePlayers = selectedPlayer === null
    ? players
    : players.filter((p) => p.id === selectedPlayer);

  const visiblePoints = selectedPlayer === null
    ? dailyPoints
    : dailyPoints.filter((d) => d.player_id === selectedPlayer);

  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <h1 className={styles.title}>포인트 관리</h1>
        <div className={styles.headerActions}>
          <button className={styles.btnSecondary} onClick={() => setShowPolicy(true)}>정책 편집</button>
          <button className={styles.btnPrimary} onClick={() => setShowAdd(true)}>+ 차감 추가</button>
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

      {loading ? (
        <div className={styles.loading}>로딩 중...</div>
      ) : (
        <>
          <PlayerPointSummary players={visiblePlayers} dailyPoints={visiblePoints} />
          <DeductionList
            deductions={deductions}
            players={players}
            onEdit={setEditTarget}
            onDelete={deleteDeduction}
          />
        </>
      )}

      <AddDeductionModal
        open={showAdd}
        onClose={() => setShowAdd(false)}
        players={players}
        dailyPoints={dailyPoints}
        defaultDate={selectedDate}
        onAdd={addDeduction}
      />

      {editTarget && (
        <EditDeductionModal
          open={true}
          onClose={() => setEditTarget(null)}
          deduction={editTarget}
          onSave={(data) => updateDeduction(editTarget.id, data)}
        />
      )}

      {showPolicy && (
        <div className={styles.overlay} data-testid="admin-point-policy-overlay">
          {/* canonical 2o (포인트 정책 편집) — no policy API exists yet
              (TRUE_FUNCTIONAL_GAP, W7.5 scope); canonical fixture used as an
              explicit pending adapter, not real policy data. */}
          <PointPolicyEditorScreen model={pointPolicyEditorFixture} onClose={() => setShowPolicy(false)} onSave={() => setShowPolicy(false)} />
        </div>
      )}
    </div>
  );
}
