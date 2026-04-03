import { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../../../api/adminApi';
import { useCycle } from '../../../hooks/useCycle';
import { useAdminToast } from '../../../hooks/useAdminToast';
import type { Deduction, DailyPoint, Player } from '../../../types/admin.types';

export function usePointView() {
  const { showToast } = useAdminToast();
  const cycle = useCycle();
  const today = new Date().toISOString().slice(0, 10);

  const [players,        setPlayers]        = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
  const [selectedDate,   setSelectedDate]   = useState(today);
  const [deductions,     setDeductions]     = useState<Deduction[]>([]);
  const [dailyPoints,    setDailyPoints]    = useState<DailyPoint[]>([]);
  const [loading,        setLoading]        = useState(true);

  // 플레이어 1회 로드
  useEffect(() => {
    const ctrl = new AbortController();
    adminApi.getPlayers(ctrl.signal)
      .then((r) => { if (!ctrl.signal.aborted) setPlayers(r.data); })
      .catch(() => {});
    return () => ctrl.abort();
  }, []);

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    try {
      // FE-09: 차감 내역은 주기 전체 조회 (날짜 필터 없음, 플레이어 필터만 적용)
      const deductionParams: { player_id?: number } = {};
      if (selectedPlayer != null) deductionParams.player_id = selectedPlayer;

      // 포인트 요약은 선택 날짜 기준
      const pointParams: { player_id?: number; date?: string } = { date: selectedDate };
      if (selectedPlayer != null) pointParams.player_id = selectedPlayer;

      const [dedsRes, ptsRes] = await Promise.all([
        adminApi.getDeductions(deductionParams, signal),
        adminApi.getDailyPoints(pointParams, signal),
      ]);
      if (!signal?.aborted) {
        // 주기 범위 내 차감만 표시
        setDeductions(dedsRes.data.filter((d) => d.date >= cycle.startDate && d.date <= cycle.endDate));
        setDailyPoints(ptsRes.data);
      }
    } catch (e) {
      if (!signal?.aborted && (e as { name?: string }).name !== 'CanceledError') {
        showToast('error', '데이터 로드 실패');
      }
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [selectedPlayer, selectedDate, cycle.startDate, cycle.endDate, showToast]);

  useEffect(() => {
    const ctrl = new AbortController();
    load(ctrl.signal);
    return () => ctrl.abort();
  }, [load]);

  const addDeduction = async (data: { player_id: number; date: string; reason: string; amount: number }) => {
    try {
      await adminApi.createDeduction(data);
      showToast('success', '차감 완료!');
      load();
    } catch { showToast('error', '차감 실패'); }
  };

  const updateDeduction = async (id: number, data: { reason?: string; amount?: number }) => {
    try {
      await adminApi.updateDeduction(id, data);
      showToast('success', '수정 완료!');
      load();
    } catch { showToast('error', '수정 실패'); }
  };

  const deleteDeduction = async (id: number) => {
    if (!confirm('차감 내역을 삭제하시겠습니까?')) return;
    try {
      await adminApi.deleteDeduction(id);
      showToast('success', '삭제 완료');
      load();
    } catch { showToast('error', '삭제 실패'); }
  };

  return {
    players, selectedPlayer, setSelectedPlayer,
    selectedDate, setSelectedDate,
    deductions, dailyPoints, loading, cycle,
    addDeduction, updateDeduction, deleteDeduction,
    reload: () => load(),
  };
}
