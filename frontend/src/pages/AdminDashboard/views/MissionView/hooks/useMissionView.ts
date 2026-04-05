import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { httpClient } from '../../../../../shared/api/httpClient';
import { getLocalToday } from '../../../../../shared/utils/dateUtils';
import { adminApi } from '../../../api/adminApi';
import { useAdminToast } from '../../../hooks/useAdminToast';
import type { Mission, Player } from '../../../types/admin.types';

interface Template {
  id: number;
  player_id: number;
  text: string;
  point: number;
  day_of_week: number;
  is_active: boolean;
  group_id: string | null;
}

export function useMissionView() {
  const { showToast } = useAdminToast();
  const today = getLocalToday();
  const [searchParams] = useSearchParams();

  // 알림 클릭으로 진입 시 ?date= 파라미터를 초기 날짜로 사용
  const initDate = searchParams.get('date') ?? today;

  const [players,        setPlayers]        = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
  const [selectedDate,   setSelectedDate]   = useState(initDate);
  const [missions,       setMissions]       = useState<Mission[]>([]);
  const [templates,      setTemplates]      = useState<Template[]>([]);
  const [loading,        setLoading]        = useState(true);

  // 플레이어 목록 (1회 로드)
  useEffect(() => {
    const ctrl = new AbortController();
    adminApi.getPlayers(ctrl.signal)
      .then((r) => { if (!ctrl.signal.aborted) setPlayers(r.data.filter((p) => p.role !== 'admin')); })
      .catch(() => {});
    return () => ctrl.abort();
  }, []);

  // 미션 로드 (player/date 변경 시)
  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    try {
      const params: { player_id?: number; date: string } = { date: selectedDate };
      if (selectedPlayer != null) params.player_id = selectedPlayer;
      const res = await adminApi.getMissions(params, signal);
      if (!signal?.aborted) setMissions(res.data);
    } catch (e) {
      if (!signal?.aborted && (e as { name?: string }).name !== 'CanceledError') {
        showToast('error', '미션 로드 실패');
      }
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [selectedPlayer, selectedDate, showToast]);

  useEffect(() => {
    const ctrl = new AbortController();
    load(ctrl.signal);
    return () => ctrl.abort();
  }, [load]);

  // 템플릿 목록 로드 (템플릿 편집 모달용)
  const loadTemplates = useCallback(async () => {
    try {
      const res = await httpClient.get<Template[]>('/api/mission-templates');
      setTemplates(res.data);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { loadTemplates(); }, [loadTemplates]);

  // ── 액션 ──
  const approve = async (mission: Mission) => {
    const newStatus = mission.status === 'proposed' ? 'active' : 'completed';
    try {
      await adminApi.updateMissionStatus(mission.id, newStatus);
      showToast('success', '승인 완료!');
      load();
    } catch { showToast('error', '처리 실패'); }
  };

  const reject = async (id: number, reason = '') => {
    try {
      // pending_approval → active 복귀 (플레이어가 다시 요청 가능)
      // 거절 사유는 msg 필드에 저장 → 플레이어 화면에 표시됨
      await adminApi.updateMission(id, {
        status: 'active',
        msg: reason || '[관리자] 다시 확인 후 재요청해주세요',
      });
      showToast('success', '거절 처리됨 (미션 재활성화)');
      load();
    } catch { showToast('error', '처리 실패'); }
  };

  const deleteMission = async (id: number, groupId?: string | null) => {
    if (groupId) {
      const ok = confirm('이 미션은 여러 플레이어에게 함께 할당되었습니다.\n모든 플레이어의 미션을 함께 삭제하시겠습니까?\n\n[확인] 전체 삭제 / [취소] 이 미션만 삭제');
      try {
        if (ok) {
          await adminApi.deleteMissionGroup(groupId);
          showToast('success', '전체 삭제 완료');
        } else {
          await adminApi.deleteMission(id);
          showToast('success', '삭제 완료');
        }
        load();
      } catch { showToast('error', '삭제 실패'); }
    } else {
      if (!confirm('미션을 삭제하시겠습니까?')) return;
      try {
        await adminApi.deleteMission(id);
        showToast('success', '삭제 완료');
        load();
      } catch { showToast('error', '삭제 실패'); }
    }
  };

  const updateMission = async (id: number, data: { text?: string; point?: number }) => {
    try {
      await adminApi.updateMission(id, data);
      showToast('success', '수정 완료!');
      load();
    } catch { showToast('error', '수정 실패'); }
  };

  const undoComplete = async (id: number) => {
    try {
      await adminApi.revertMission(id);
      showToast('success', '복구 완료 (포인트 환수됨)');
      load();
    } catch { showToast('error', '처리 실패'); }
  };

  const createMission = async (data: { player_id: number; date: string; text: string; point: number; group_id?: string }) => {
    try {
      await adminApi.createMission(data);
      showToast('success', '미션 추가!');
      load();
    } catch { showToast('error', '추가 실패'); }
  };

  // 반복 미션 편집을 위해 미션에서 템플릿 역추적 (player_id + text + point 매칭)
  const findTemplateForMission = (mission: Mission): Template | null => {
    return templates.find(
      t => t.player_id === mission.player_id &&
           t.text      === mission.text &&
           t.point     === mission.point &&
           !t.is_active === false
    ) ?? null;
  };

  return {
    players, selectedPlayer, setSelectedPlayer,
    selectedDate, setSelectedDate,
    proposedMissions: missions.filter((m) => m.status === 'proposed'),
    regularMissions:  missions.filter((m) => m.status !== 'proposed'),
    loading,
    approve, reject, deleteMission, updateMission, undoComplete, createMission,
    reload:               () => { load(); loadTemplates(); },
    findTemplateForMission,
  };
}
