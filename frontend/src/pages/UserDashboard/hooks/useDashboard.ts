import { useState, useCallback, useEffect } from 'react';
import { useAuthStore } from '../../../shared/stores/useAuthStore';
import {
  dashboardApi,
  MissionResponse,
  CheerResponse,
  FeedbackResponse,
  DeductionResponse,
  DailyPointResponse,
  PointCycleSummary,
  PlayerResponse,
} from '../api/dashboardApi';

export interface SenderConfig {
  key: string;
  label: string;
  color: string;
  emoji: string;
}

const SENDERS_FALLBACK: SenderConfig[] = [
  { key: 'dad', label: '아빠', color: 'var(--blue)', emoji: '👨' },
  { key: 'mom', label: '엄마', color: '#db2777', emoji: '👩' },
];

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

  // 포인트 주기
  const [pointCycle, setPointCycle] = useState<string>('weekly');
  const [cycleSummary, setCycleSummary] = useState<PointCycleSummary | null>(null);

  // UI 상태
  const [activeTab, setActiveTab] = useState<'missions' | 'proposal' | 'feedback'>('missions');
  const [activeNav, setActiveNav] = useState<'home' | 'ranking'>('home');
  const [deductOpen, setDeductOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // 레벨 설정 (app_configs에서 로드, null = 로드 전/실패)
  const [levelThresholds, setLevelThresholds] = useState<Record<string, number> | null>(null);
  const [configError, setConfigError] = useState(false);

  // 응원 발신자 목록 (app_configs cheer.senders)
  const [senders, setSenders] = useState<SenderConfig[]>([]);

  // 부모 사진 (app_configs photos.{sender})
  const [parentPhotos, setParentPhotos] = useState<Record<string, string>>({});

  // 플레이어 사진 (DB players.photo)
  const [playerPhoto, setPlayerPhoto] = useState<string | null>(null);

  // 플레이어 상태 메시지 (DB players.status_msg)
  const [playerStatusMsg, setPlayerStatusMsg] = useState<string>('');

  // 전체 플레이어 목록 (대화하기 탭용)
  const [allPlayers, setAllPlayers] = useState<PlayerResponse[]>([]);

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

  // 포인트 주기 설정 로드 (최초 1회)
  useEffect(() => {
    const controller = new AbortController();
    dashboardApi.getPointCycle(controller.signal)
      .then((res) => { if (res.data.value) setPointCycle(res.data.value); })
      .catch(() => { /* 실패 시 기본값 weekly 유지 */ });
    return () => controller.abort();
  }, []);

  // 날짜/플레이어/주기 변경 시 주기별 집계 로드
  useEffect(() => {
    if (!player) return;
    const controller = new AbortController();
    dashboardApi.getPointCycleSummary(player.id, selectedDate, pointCycle, controller.signal)
      .then((res) => { if (!controller.signal.aborted) setCycleSummary(res.data); })
      .catch(() => {});
    return () => controller.abort();
  }, [player, selectedDate, pointCycle]);

  // 플레이어 사진 로드 (로그인 후 최초 1회)
  useEffect(() => {
    if (!player) return;
    const ctrl = new AbortController();
    dashboardApi.getMe(ctrl.signal)
      .then((res) => {
        if (!ctrl.signal.aborted) {
          setPlayerPhoto(res.data.photo ?? null);
          setPlayerStatusMsg(res.data.status_msg ?? '');
        }
      })
      .catch(() => {});
    return () => ctrl.abort();
  }, [player?.id]);

  // 전체 플레이어 목록 로드 (대화하기 탭용, 최초 1회)
  useEffect(() => {
    dashboardApi.getPlayers()
      .then(res => setAllPlayers(res.data))
      .catch(() => {});
  }, []);

  // 레벨 임계치 + senders 로드 (최초 1회)
  useEffect(() => {
    dashboardApi.getConfig('level.thresholds')
      .then(res => {
        if (res.data.value) setLevelThresholds(JSON.parse(res.data.value));
        else setConfigError(true);
      })
      .catch(() => setConfigError(true));

    dashboardApi.getConfig('cheer.senders')
      .then(res => {
        if (res.data.value) setSenders(JSON.parse(res.data.value));
        else setSenders(SENDERS_FALLBACK);
      })
      .catch(() => setSenders(SENDERS_FALLBACK));
  }, []);

  // 부모 사진 로드 (senders 확정 후)
  useEffect(() => {
    if (!senders.length) return;
    Promise.all(senders.map(s => dashboardApi.getConfig(`photos.${s.key}`).catch(() => null)))
      .then(results => {
        const photos: Record<string, string> = {};
        results.forEach((res, i) => {
          if (res?.data?.value) photos[senders[i].key] = res.data.value;
        });
        setParentPhotos(photos);
      })
      .catch(() => {});
  }, [senders]);

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

  // 피드백 전송 (recipient: 수신자 이름)
  const sendFeedback = useCallback(async (msg: string, recipient?: string) => {
    if (!player) return;
    await dashboardApi.sendFeedback({ player_id: player.id, date: selectedDate, msg, recipient });
    await refreshData();
  }, [player, selectedDate, refreshData]);

  // 피드백 답장 전송 (발신자 = 로그인한 플레이어 이름)
  const sendReply = useCallback(async (feedbackId: number, text: string) => {
    if (!player) return;
    await dashboardApi.sendReply({ feedback_id: feedbackId, sender: player.name, text });
    await refreshData();
  }, [player, refreshData]);

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
    pointCycle, cycleSummary,
    activeTab, activeNav, deductOpen, loading, levelThresholds, configError, senders, parentPhotos, playerPhoto, playerStatusMsg, allPlayers,
    // 파생
    myProposals, activeMissions, totalDeducted, totalAllocated, pendingPoints,
    // 액션
    setSelectedDate, setActiveTab, setActiveNav, setDeductOpen,
    quickDate, requestApproval, proposeMission, sendFeedback, sendReply, refreshData,
  };
}
