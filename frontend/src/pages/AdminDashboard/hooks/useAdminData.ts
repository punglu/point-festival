import { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../api/adminApi';
import { useCycle } from './useCycle';
import { getLocalToday } from '../../../shared/utils/dateUtils';
import { useAdminToast } from './useAdminToast';
import { httpClient } from '../../../shared/api/httpClient';
import type {
  Player, Mission, Notification, DailyPoint,
  DashboardStats, MissionRankItem,
} from '../types/admin.types';

export function useAdminData() {
  const cycle = useCycle();
  const { showToast } = useAdminToast();
  const [players,       setPlayers]       = useState<Player[]>([]);
  const [missions,      setMissions]      = useState<Mission[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [dailyPoints,   setDailyPoints]   = useState<DailyPoint[]>([]);
  const [loading,       setLoading]       = useState(true);

  const loadDashboardData = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    try {
      // FE-01: 현재 주기 범위로 미션 조회 (스탯 카드 범위 통일)
      const [playersRes, missionsRes, notifsRes] = await Promise.all([
        adminApi.getPlayers(signal),
        adminApi.getMissions({ date_from: cycle.startDate, date_to: cycle.endDate }, signal),
        adminApi.getNotifications(signal),
      ]);
      if (signal?.aborted) return;

      setPlayers(playersRes.data);
      setMissions(missionsRes.data);
      setNotifications(notifsRes.data);

      // 각 플레이어별 주기 포인트 조회
      const pointPromises = playersRes.data.map((p) =>
        adminApi.getDailyPointsRange(p.id, cycle.startDate, cycle.endDate, signal)
      );
      const pointResults = await Promise.all(pointPromises);
      if (signal?.aborted) return;
      setDailyPoints(pointResults.flatMap((r) => r.data));
    } catch (err) {
      if ((err as { name?: string }).name !== 'CanceledError') {
        console.error('대시보드 데이터 로드 실패:', err);
      }
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [cycle.startDate, cycle.endDate]);

  useEffect(() => {
    const controller = new AbortController();
    loadDashboardData(controller.signal);
    return () => controller.abort();
  }, [loadDashboardData]);

  // Lazy Init: 마운트 시 1회 — 오늘의 템플릿 미션 자동 생성
  useEffect(() => {
    const controller = new AbortController();
    httpClient.post('/api/mission-templates/generate', {}, { signal: controller.signal })
      .catch(() => {}); // 실패해도 대시보드 사용에 영향 없음
    return () => controller.abort();
  }, []);

  // ── 대시보드 통계 파생 ──
  const today = getLocalToday();
  const stats: DashboardStats = {
    totalActiveMissions: missions.filter((m) => m.status === 'active').length,
    pendingApproval:     missions.filter((m) => m.status === 'pending_approval').length,
    completedThisWeek:   missions.filter((m) =>
      m.status === 'completed' && m.date >= cycle.startDate && m.date <= cycle.endDate
    ).length,
    totalPointsIssued:   dailyPoints.reduce((sum, dp) => sum + dp.earned, 0),
    todayNewMissions:    missions.filter((m) => m.date === today).length,
    weeklyGoal:          15,
  };

  // ── 미션 랭킹 파생 (완료 미션 기준) ──
  const missionRanking: MissionRankItem[] = (() => {
    const countMap: Record<string, { total: number; players: Record<string, number> }> = {};
    missions
      .filter((m) => m.status === 'completed')
      .forEach((m) => {
        const playerName = players.find((p) => p.id === m.player_id)?.name ?? '?';
        if (!countMap[m.text]) countMap[m.text] = { total: 0, players: {} };
        countMap[m.text].total++;
        countMap[m.text].players[playerName] = (countMap[m.text].players[playerName] ?? 0) + 1;
      });
    return Object.entries(countMap)
      .map(([text, data]) => ({ text, totalCount: data.total, playerCounts: data.players }))
      .sort((a, b) => b.totalCount - a.totalCount)
      .slice(0, 8);
  })();

  const unreadNotifCount = notifications.filter((n) => !n.is_read).length;

  const reload = useCallback(() => {
    const controller = new AbortController();
    loadDashboardData(controller.signal);
  }, [loadDashboardData]);

  // ── 승인/거절 액션 ──
  const approveMission = async (id: number) => {
    try {
      await adminApi.updateMissionStatus(id, 'completed');
      showToast('success', '승인 완료!');
      reload();
    } catch { showToast('error', '처리 실패'); }
  };

  const rejectMission = async (id: number, reason = '') => {
    try {
      await adminApi.updateMissionStatus(id, 'rejected', reason || undefined);
      showToast('success', '거절 처리됨');
      reload();
    } catch { showToast('error', '처리 실패'); }
  };

  return {
    players, missions, notifications, dailyPoints,
    stats, missionRanking, unreadNotifCount,
    cycle, loading, reload,
    approveMission, rejectMission,
  };
}
