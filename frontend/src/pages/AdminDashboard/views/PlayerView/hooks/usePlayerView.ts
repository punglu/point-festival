import { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../../../api/adminApi';
import { useAdminToast } from '../../../hooks/useAdminToast';
import type { Player, Mission, LoginLog } from '../../../types/admin.types';

export function usePlayerView() {
  const { showToast } = useAdminToast();

  const [players,   setPlayers]   = useState<Player[]>([]);
  const [missions,  setMissions]  = useState<Mission[]>([]);
  const [loginLogs, setLoginLogs] = useState<LoginLog[]>([]);
  const [loading,   setLoading]   = useState(true);

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    try {
      const [playersRes, logsRes] = await Promise.all([
        adminApi.getPlayers(signal),
        adminApi.getLoginLogs({ limit: 20 }, signal),
      ]);
      if (signal?.aborted) return;
      setPlayers(playersRes.data);
      setLoginLogs(logsRes.data);

      // 미션 달성률 계산용: 각 플레이어 전체 미션 로드
      const missionResults = await Promise.all(
        playersRes.data.map((p) => adminApi.getMissions({ player_id: p.id }, signal))
      );
      if (!signal?.aborted) {
        setMissions(missionResults.flatMap((r) => r.data));
      }
    } catch (e) {
      if (!signal?.aborted && (e as { name?: string }).name !== 'CanceledError') {
        showToast('error', '데이터 로드 실패');
      }
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    const ctrl = new AbortController();
    load(ctrl.signal);
    return () => ctrl.abort();
  }, [load]);

  const updatePlayer = async (id: number, data: { name?: string; status_msg?: string; photo?: string }) => {
    try {
      await adminApi.updatePlayer(id, data);
      showToast('success', '업데이트 완료!');
      load();
    } catch { showToast('error', '업데이트 실패'); }
  };

  const changePin = async (id: number, pin: string) => {
    try {
      await adminApi.changePlayerPin(id, pin);
      showToast('success', 'PIN 변경 완료!');
    } catch { showToast('error', 'PIN 변경 실패'); }
  };

  const createPlayer = async (data: { name: string; pin: string }) => {
    await adminApi.createPlayer(data);
    showToast('success', '플레이어 추가 완료!');
    load();
  };

  const deletePlayer = async (id: number) => {
    if (!confirm('플레이어를 삭제하시겠습니까? 관련 데이터는 유지됩니다.')) return;
    try {
      await adminApi.deletePlayer(id);
      showToast('success', '플레이어 삭제 완료');
      load();
    } catch { showToast('error', '삭제 실패'); }
  };

  // 플레이어별 달성률 계산
  const achievementRate = (playerId: number): number => {
    const pm = missions.filter((m) => m.player_id === playerId);
    if (pm.length === 0) return 0;
    const completed = pm.filter((m) => m.status === 'completed').length;
    return Math.round((completed / pm.length) * 100);
  };

  return {
    players, missions, loginLogs, loading,
    updatePlayer, changePin, createPlayer, deletePlayer, achievementRate,
    reload: () => load(),
  };
}
