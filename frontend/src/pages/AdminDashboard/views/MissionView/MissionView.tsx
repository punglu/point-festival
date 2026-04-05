import { useState } from 'react';
import styles from './MissionView.module.css';
import { useMissionView } from './hooks/useMissionView';
import { httpClient } from '../../../../shared/api/httpClient';
import MissionCard from './components/MissionCard';
import MissionCardEdit from './components/MissionCardEdit';
import ProposedMissionSection from './components/ProposedMissionSection';
import NewMissionModal from './components/NewMissionModal';
import WeeklyGrid from './components/WeeklyGrid';
import TemplateModal from './components/TemplateModal';
import TemplateManager from './components/TemplateManager';
import ImportMissionModal from './components/ImportMissionModal';
import type { Mission } from '../../types/admin.types';

interface Template {
  id: number;
  player_id: number;
  text: string;
  point: number;
  day_of_week: number;
  is_active: boolean;
  group_id: string | null;
}

export default function MissionView() {
  const {
    players, selectedPlayer, setSelectedPlayer,
    selectedDate, setSelectedDate,
    proposedMissions, regularMissions, loading,
    approve, reject, deleteMission, updateMission, undoComplete, createMission,
    reload, findTemplateForMission,
  } = useMissionView();

  const [editingId,            setEditingId]            = useState<number | null>(null);
  const [addMissionOpen,       setAddMissionOpen]       = useState(false);
  const [templateModalOpen,    setTemplateModalOpen]    = useState(false);
  const [templateManagerOpen,  setTemplateManagerOpen]  = useState(false);
  const [importModalOpen,      setImportModalOpen]      = useState(false);
  const [editingTemplate,      setEditingTemplate]      = useState<Template | null>(null);

  const handleGridCellSelect = (playerId: number, date: string) => {
    setSelectedDate(date);
    setSelectedPlayer(playerId);
  };

  const handleBulkApprove = async (playerId: number, date: string) => {
    try {
      await httpClient.post('/api/admin/missions/bulk-approve', null, {
        params: { player_id: playerId, date },
      });
      reload();
    } catch { /* ignore */ }
  };

  const handleEditTemplate = (mission: Mission) => {
    const tmpl = findTemplateForMission(mission);
    if (tmpl) {
      setEditingTemplate(tmpl);
    } else {
      // 템플릿을 찾지 못한 경우 미션 정보로 기본값 구성
      setEditingTemplate({
        id: 0,
        player_id: mission.player_id,
        text: mission.text,
        point: mission.point,
        day_of_week: 127,
        is_active: true,
        group_id: null,
      });
    }
    setTemplateModalOpen(true);
  };

  return (
    <div className={styles.view}>
      {/* 상단 타이틀 */}
      <div className={styles.header}>
        <h1 className={styles.title}>미션 관리</h1>
      </div>

      {/* 주간 그리드 */}
      <WeeklyGrid
        onSelectCell={handleGridCellSelect}
        onBulkApprove={handleBulkApprove}
      />

      {/* 액션 바 */}
      <div className={styles.actionBar}>
        {/* 플레이어 필터 */}
        <select
          value={selectedPlayer ?? 'all'}
          onChange={(e) => setSelectedPlayer(e.target.value === 'all' ? null : Number(e.target.value))}
          className={styles.actionBtn}
        >
          <option value="all">전체</option>
          {players.map(p => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>

        {/* 날짜 선택 */}
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className={styles.actionBtn}
        />

        {/* 과거 미션 가져오기 */}
        <button className={styles.actionBtn} onClick={() => setImportModalOpen(true)}>
          📥 과거 미션 가져오기
        </button>

        {/* 일반 미션 추가 */}
        <button className={styles.actionBtn} onClick={() => setAddMissionOpen(true)}>
          ➕ 일반 미션 추가
        </button>

        {/* 반복미션 관리 */}
        <button className={styles.actionBtn} onClick={() => setTemplateManagerOpen(true)}>
          🔄 반복미션 관리
        </button>
      </div>

      {/* 제안 미션 섹션 */}
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

      {/* 전체 승인 버튼 */}
      {regularMissions.some(m => m.status === 'pending_approval') && selectedPlayer !== null && (
        <button
          className={styles.bulkApproveBtn}
          onClick={() => handleBulkApprove(selectedPlayer, selectedDate)}
        >
          전체 승인
        </button>
      )}

      {/* 미션 카드 목록 */}
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
                onEditTemplate={handleEditTemplate}
                onUndoComplete={undoComplete}
              />
            )
          )}
        </div>
      )}

      {/* 일반 미션 추가 모달 */}
      <NewMissionModal
        open={addMissionOpen}
        onClose={() => setAddMissionOpen(false)}
        players={players}
        defaultDate={selectedDate}
        onCreate={createMission}
      />

      {/* 반복미션 관리 모달 */}
      <TemplateManager
        isOpen={templateManagerOpen}
        onClose={() => setTemplateManagerOpen(false)}
        players={players}
        onOpenCreateModal={() => {
          setTemplateManagerOpen(false);
          setEditingTemplate(null);
          setTemplateModalOpen(true);
        }}
        onOpenEditModal={(template) => {
          setTemplateManagerOpen(false);
          setEditingTemplate({ ...template, group_id: template.group_id ?? null });
          setTemplateModalOpen(true);
        }}
      />

      {/* 반복 미션 추가/편집 모달 */}
      <TemplateModal
        isOpen={templateModalOpen}
        onClose={() => { setTemplateModalOpen(false); setEditingTemplate(null); }}
        onSuccess={() => { reload(); setTemplateModalOpen(false); setEditingTemplate(null); }}
        players={players}
        editingTemplate={editingTemplate}
      />

      {/* 과거 미션 가져오기 모달 */}
      <ImportMissionModal
        isOpen={importModalOpen}
        onClose={() => setImportModalOpen(false)}
        onSuccess={() => { reload(); setImportModalOpen(false); }}
        players={players}
        targetDate={selectedDate}
      />
    </div>
  );
}
