import { useState, useCallback, useEffect } from 'react';
import { useAuthStore } from '../../../shared/stores/useAuthStore';
import {
  dashboardApi,
  MissionResponse,
  CheerResponse,
  FeedbackResponse,
  DeductionResponse,
  DailyPointResponse,
} from '../api/dashboardApi';

function getToday(): string {
  return new Date().toISOString().slice(0, 10);
}

export function useDashboard() {
  const { player } = useAuthStore();

  // 날짜
  const [selectedDate, setSelectedDate] = useState(getToday());

  // 데이터
  const [missions, setMissions] = useState<MissionResponse[]>([]);
  const [cheers, setCheers] = useState<CheerResponse[]>([]);
  const [feedbacks, setFeedbacks] = useState<FeedbackResponse[]>([]);
  const [deductions, setDeductions] = useState<DeductionResponse[]>([]);
  const [dailyPoint, setDailyPoint] = useState<DailyPointResponse | null>(null);

  // UI 상태
  const [activeTab, setActiveTab] = useState<'missions' | 'proposal' | 'feedback'>('missions');
  const [activeNav, setActiveNav] = useState<'home' | 'ranking'>('home');
  const [deductOpen, setDeductOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // 레벨 설정 (app_configs에서 로드, 실패 시 기본값 유지)
  const [levelThresholds, setLevelThresholds] = useState<Record<string, number>>({
    '1': 0, '2': 50, '3': 150, '4': 300, '5': 500,
  });

  // 날짜/플레이어 변경 시 데이터 로드 — AbortController로 race condition 방지
  useEffect(() => {
    if (!player) return;

    const abortController = new AbortController();

    const loadData = async () => {
      setLoading(true);
      try {
        const data = await dashboardApi.fetchDayData(
          player.id,
          selectedDate,
          abortController.signal,
        );
        if (!abortController.signal.aborted) {
          setMissions(data.missions);
          setCheers(data.cheers);
          setFeedbacks(data.feedbacks);
          setDeductions(data.deductions);
          setDailyPoint(data.dailyPoint);
        }
      } catch (err) {
        if (!abortController.signal.aborted) {
          console.error('데이터 로드 실패:', err);
        }
      } finally {
        if (!abortController.signal.aborted) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      abortController.abort();
    };
  }, [player, selectedDate]);

  // 레벨 임계치 로드 (최초 1회)
  useEffect(() => {
    dashboardApi.getConfig('level.thresholds')
      .then(res => {
        if (res.data.value) setLevelThresholds(JSON.parse(res.data.value));
      })
      .catch(() => {}); // 실패 시 기본값 유지
  }, []);

  // 액션 후 갱신용 (사용자 명시 액션 — abort 불필요)
  const refreshData = useCallback(async () => {
    if (!player) return;
    setLoading(true);
    try {
      const data = await dashboardApi.fetchDayData(player.id, selectedDate);
      setMissions(data.missions);
      setCheers(data.cheers);
      setFeedbacks(data.feedbacks);
      setDeductions(data.deductions);
      setDailyPoint(data.dailyPoint);
    } catch (err) {
      console.error('데이터 갱신 실패:', err);
    } finally {
      setLoading(false);
    }
  }, [player, selectedDate]);

  // 미션 승인 요청
  const requestApproval = useCallback(async (missionId: number) => {
    await dashboardApi.requestApproval(missionId);
    await refreshData();
  }, [refreshData]);

  // 미션 제안
  const proposeMission = useCallback(async (text: string, point: number, reason?: string) => {
    if (!player) return;
    await dashboardApi.proposeMission({
      player_id: player.id,
      date: selectedDate,
      text,
      point,
      proposed_by: player.name,
      proposal_reason: reason,
    });
    await refreshData();
  }, [player, selectedDate, refreshData]);

  // 피드백 전송
  const sendFeedback = useCallback(async (msg: string) => {
    if (!player) return;
    await dashboardApi.sendFeedback({ player_id: player.id, date: selectedDate, msg });
    await refreshData();
  }, [player, selectedDate, refreshData]);

  // 날짜 퀵 선택 (offset: -1=어제, 0=오늘, 1=내일)
  const quickDate = useCallback((offset: number) => {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    setSelectedDate(d.toISOString().slice(0, 10));
  }, []);

  // 파생 데이터
  const myProposals = missions.filter(
    m => m.status === 'proposed' && m.proposed_by === player?.name,
  );
  const activeMissions = missions.filter(m => m.status !== 'proposed');
  const totalDeducted = deductions.reduce((sum, d) => sum + d.amount, 0);
  const totalAllocated = activeMissions.reduce(
    (sum, m) => (m.status !== 'rejected' ? sum + m.point : sum), 0,
  );
  const pendingPoints = activeMissions
    .filter(m => m.status === 'active')
    .reduce((sum, m) => sum + m.point, 0);

  return {
    // 상태
    player, selectedDate, missions, cheers, feedbacks, deductions, dailyPoint,
    activeTab, activeNav, deductOpen, loading, levelThresholds,
    // 파생
    myProposals, activeMissions, totalDeducted, totalAllocated, pendingPoints,
    // 액션
    setSelectedDate, setActiveTab, setActiveNav, setDeductOpen,
    quickDate, requestApproval, proposeMission, sendFeedback, refreshData,
  };
}
