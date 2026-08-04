import { useState } from 'react';
import { getLocalToday, shiftDay } from '../../../../../shared/utils/dateUtils';
import AdminModal from '../../../components/AdminModal/AdminModal';
import { POINT_QUICK_VALUES } from '../../../constants/admin.constants';
import { MissionCreateFormScreen } from '../../../../../screens/admin/MissionCreateForm';
import type { MissionCreateFormDateMode, MissionCreateFormSubmitPayload } from '../../../../../screens/admin/MissionCreateForm';
import type { Player } from '../../../types/admin.types';

interface Props {
  open:        boolean;
  onClose:     () => void;
  players:     Player[];
  defaultDate: string;
  onCreate:    (data: { player_id: number; date: string; text: string; point: number; group_id?: string }) => Promise<void>;
}

// canonical 2l (미션 만들기 폼) -- W7.4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001:
// this modal now renders the expanded canonical Screen for its body;
// AdminModal keeps owning the real overlay/title/close/Escape chrome it
// always did. The real multi-assignee fan-out (shared group_id when 2+
// assignees, matching the real createMission contract) stays here, in the
// Product Container -- the canonical Screen only emits one typed payload
// per submit and never calls the API itself.
export default function NewMissionModal({ open, onClose, players, defaultDate, onCreate }: Props) {
  const today    = getLocalToday();
  const tomorrow = shiftDay(today, 1);

  const [selectedAssigneeIds, setSelectedAssigneeIds] = useState<number[]>([]);
  const [title,       setTitle]       = useState('');
  const [description, setDescription] = useState('');
  const [point,        setPoint]       = useState(10);
  const [dateMode,     setDateMode]    = useState<MissionCreateFormDateMode>('today');
  const [customDate,   setCustomDate]  = useState(defaultDate);
  const [submitting,   setSubmitting]  = useState(false);

  const toggleAssignee = (id: number) => {
    setSelectedAssigneeIds((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  const toggleAll = () => {
    setSelectedAssigneeIds((prev) =>
      prev.length === players.length ? [] : players.map((p) => p.id)
    );
  };

  const resolveDate = (mode: MissionCreateFormDateMode, custom: string) =>
    mode === 'today' ? today : mode === 'tomorrow' ? tomorrow : custom;

  const canSubmit =
    title.trim() !== '' &&
    selectedAssigneeIds.length > 0 &&
    (dateMode !== 'custom' || customDate !== '');

  const handleCreate = async (payload: MissionCreateFormSubmitPayload) => {
    if (payload.title.trim() === '' || payload.assigneeIds.length === 0) return;
    setSubmitting(true);
    try {
      // real Mission schema has no separate description field -- folded
      // into the free-text `text` when present, rather than dropped.
      const text = payload.description.trim()
        ? `${payload.title.trim()} - ${payload.description.trim()}`
        : payload.title.trim();
      const date = resolveDate(payload.dateMode, payload.customDate);
      // 2명 이상에게 할당 시 같은 group_id 공유 → 이후 일괄 삭제 가능
      const groupId = payload.assigneeIds.length > 1 ? crypto.randomUUID() : undefined;
      await Promise.all(
        payload.assigneeIds.map((pid) =>
          onCreate({ player_id: pid, date, text, point: payload.point, group_id: groupId })
        )
      );
      setTitle(''); setDescription(''); setPoint(10); setSelectedAssigneeIds([]); setDateMode('today');
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AdminModal open={open} onClose={onClose} title="새 미션 추가" width={720}>
      <MissionCreateFormScreen
        embedded
        model={{
          assignees: players.map((p) => ({ id: p.id, name: p.name })),
          selectedAssigneeIds,
          title,
          description,
          point,
          quickPointOptions: [...POINT_QUICK_VALUES],
          dateMode,
          todayLabel: '오늘',
          tomorrowLabel: '내일',
          customDate,
          submitting,
          canSubmit,
        }}
        onToggleAssignee={toggleAssignee}
        onToggleAllAssignees={toggleAll}
        onTitleChange={setTitle}
        onDescriptionChange={setDescription}
        onPointChange={setPoint}
        onQuickPointSelect={setPoint}
        onDateModeChange={setDateMode}
        onCustomDateChange={setCustomDate}
        onCancel={onClose}
        onCreate={(payload) => void handleCreate(payload)}
      />
    </AdminModal>
  );
}
