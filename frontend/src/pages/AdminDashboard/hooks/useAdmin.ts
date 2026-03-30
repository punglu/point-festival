import { useState, useCallback, useEffect } from 'react';
import { dashboardApi, PlayerResponse } from '../../UserDashboard/api/dashboardApi';

export type AdminTab = 'missions' | 'points' | 'cheer' | 'players' | 'more';
export type MoreTab = 'notifications' | 'feedbacks' | 'configs';

function getToday(): string {
  return new Date().toISOString().slice(0, 10);
}

export function useAdmin() {
  const [players, setPlayers] = useState<PlayerResponse[]>([]);
  const [selectedPlayerId, setSelectedPlayerId] = useState<number | null>(null);
  const [selectedDate, setSelectedDate] = useState(getToday());
  const [activeTab, setActiveTab] = useState<AdminTab>('missions');
  const [activeMoreTab, setActiveMoreTab] = useState<MoreTab>('notifications');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 플레이어 목록 로드 (최초 1회, AbortController 적용)
  useEffect(() => {
    const abortController = new AbortController();

    const loadPlayers = async () => {
      setLoading(true);
      try {
        const res = await dashboardApi.getPlayers();
        if (!abortController.signal.aborted) {
          setPlayers(res.data);
          if (res.data.length > 0) {
            setSelectedPlayerId(res.data[0].id);
          }
        }
      } catch (err) {
        if (!abortController.signal.aborted) {
          setError('플레이어 목록 로드 실패');
          console.error(err);
        }
      } finally {
        if (!abortController.signal.aborted) {
          setLoading(false);
        }
      }
    };

    loadPlayers();

    return () => {
      abortController.abort();
    };
  }, []);

  const quickDate = useCallback((offset: number) => {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    setSelectedDate(d.toISOString().slice(0, 10));
  }, []);

  return {
    players,
    selectedPlayerId,
    selectedDate,
    activeTab,
    activeMoreTab,
    loading,
    error,
    setSelectedPlayerId,
    setSelectedDate,
    setActiveTab,
    setActiveMoreTab,
    quickDate,
  };
}
