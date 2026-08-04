import { useMemo, useState } from 'react';
import { useMissionView } from './hooks/useMissionView';
import { httpClient } from '../../../../shared/api/httpClient';
import MissionCard from './components/MissionCard';
import MissionCardEdit from './components/MissionCardEdit';
import NewMissionModal from './components/NewMissionModal';
import WeeklyGrid from './components/WeeklyGrid';
import ProposedMissionSection from './components/ProposedMissionSection';
import TemplateModal from './components/TemplateModal';
import TemplateManager from './components/TemplateManager';
import ImportMissionModal from './components/ImportMissionModal';
import { MissionManagementScreen } from '../../../../screens/admin/MissionManagement';
import type { MissionManagementFilterStatus, MissionManagementModel } from '../../../../screens/admin/MissionManagement';
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

// canonical 2e (미션 관리) -- W7.4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001:
// this Product Container now renders the expanded canonical Screen.
// WeeklyGrid keeps fetching/rendering itself unchanged and is composed as
// a slot (a Canonical Screen must never fetch directly). Every row's real
// content is still MissionCard/MissionCardEdit exactly as before -- the
// Screen's own AdminDataGrid only supplies the grid chrome, it does not
// reimplement per-status conditional actions or inline-edit logic.
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
  // 실제 canonical 2e mockup에 존재했지만 실제 제품에는 없던 상태 필터/검색 --
  // 이미 로드된 regularMissions에 대한 순수 클라이언트 필터이므로 새 API 없이
  // 실제로 동작하게 만든다 (신규 backend 요청 없음).
  const [filterStatus,         setFilterStatus]         = useState<MissionManagementFilterStatus>('all');
  const [searchQuery,          setSearchQuery]          = useState('');

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

  const filteredMissions = useMemo(() => {
    return regularMissions.filter((m) => {
      if (filterStatus === 'active' && m.status !== 'active') return false;
      if (filterStatus === 'completed' && m.status !== 'completed') return false;
      if (searchQuery.trim() && !m.text.toLowerCase().includes(searchQuery.trim().toLowerCase())) return false;
      return true;
    });
  }, [regularMissions, filterStatus, searchQuery]);

  const model: MissionManagementModel = useMemo(() => {
    const pendingCount = regularMissions.filter((m) => m.status === 'pending_approval').length + proposedMissions.length;
    return {
      stats: [
        { label: '전체 미션', value: `${regularMissions.length + proposedMissions.length}개` },
        { label: '진행 중', value: `${regularMissions.filter((m) => m.status === 'active').length}개` },
        { label: '승인 대기', value: `${pendingCount}개` },
      ],
      playerOptions: players.map((p) => ({ id: p.id, name: p.name })),
      selectedPlayerId: selectedPlayer,
      selectedDate,
      filterStatus,
      searchQuery,
      rows: filteredMissions.map((m) => ({
        id: m.id,
        content: editingId === m.id ? (
          <MissionCardEdit
            mission={m}
            onSave={(data) => { updateMission(m.id, data); setEditingId(null); }}
            onCancel={() => setEditingId(null)}
          />
        ) : (
          <MissionCard
            mission={m}
            players={players}
            onApprove={approve}
            onReject={(id) => reject(id)}
            onDelete={deleteMission}
            onEdit={() => setEditingId(m.id)}
            onEditTemplate={handleEditTemplate}
            onUndoComplete={undoComplete}
          />
        ),
      })),
      canBulkApprove: selectedPlayer !== null && regularMissions.some((m) => m.status === 'pending_approval'),
      loading,
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    players, selectedPlayer, selectedDate, filterStatus, searchQuery,
    proposedMissions, regularMissions, filteredMissions, editingId, loading,
  ]);

  return (
    <>
      <MissionManagementScreen
        model={model}
        embedded
        weekGridSlot={<WeeklyGrid onSelectCell={handleGridCellSelect} onBulkApprove={handleBulkApprove} />}
        proposedSlot={proposedMissions.length > 0 && (
          <ProposedMissionSection
            missions={proposedMissions}
            players={players}
            onApprove={approve}
            onReject={(id) => reject(id)}
          />
        )}
        onSelectPlayer={setSelectedPlayer}
        onSelectDate={setSelectedDate}
        onFilterStatus={setFilterStatus}
        onSearch={setSearchQuery}
        onOpenImport={() => setImportModalOpen(true)}
        onOpenAdd={() => setAddMissionOpen(true)}
        onOpenTemplates={() => setTemplateManagerOpen(true)}
        onBulkApprove={() => { if (selectedPlayer !== null) void handleBulkApprove(selectedPlayer, selectedDate); }}
      />

      {/* 일반 미션 추가 모달 (canonical 2l 내장) */}
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
    </>
  );
}
