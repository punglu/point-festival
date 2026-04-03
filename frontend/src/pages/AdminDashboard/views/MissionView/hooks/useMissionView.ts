import { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../../../api/adminApi';
import { useAdminToast } from '../../../hooks/useAdminToast';
import type { Mission, Player } from '../../../types/admin.types';

export function useMissionView() {
  const { showToast } = useAdminToast();
  const today = new Date().toISOString().slice(0, 10);

  const [players,        setPlayers]        = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
  const [selectedDate,   setSelectedDate]   = useState(today);
  const [missions,       setMissions]       = useState<Mission[]>([]);
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
      await adminApi.updateMissionStatus(id, 'rejected', reason || undefined);
      showToast('success', '거절 처리됨');
      load();
    } catch { showToast('error', '처리 실패'); }
  };

  const deleteMission = async (id: number) => {
    if (!confirm('미션을 삭제하시겠습니까?')) return;
    try {
      await adminApi.deleteMission(id);
      showToast('success', '삭제 완료');
      load();
    } catch { showToast('error', '삭제 실패'); }
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
      await adminApi.updateMissionStatus(id, 'active');
      showToast('success', '완료 취소됨');
      load();
    } catch { showToast('error', '처리 실패'); }
  };

  const createMission = async (data: { player_id: number; date: string; text: string; point: number }) => {
    try {
      await adminApi.createMission(data);
      showToast('success', '미션 추가!');
      load();
    } catch { showToast('error', '추가 실패'); }
  };

  const batchCopy = async (data: { player_id: number; source_date: string; target_date: string; mission_ids: number[] }) => {
    try {
      await adminApi.batchCopyMissions(data);
      showToast('success', '복제 완료!');
      load();
    } catch { showToast('error', '복제 실패'); }
  };

  return {
    players, selectedPlayer, setSelectedPlayer,
    selectedDate, setSelectedDate,
    proposedMissions: missions.filter((m) => m.status === 'proposed'),
    regularMissions:  missions.filter((m) => m.status !== 'proposed'),
    loading,
    approve, reject, deleteMission, updateMission, undoComplete, createMission, batchCopy,
    reload: () => load(),
  };
}
