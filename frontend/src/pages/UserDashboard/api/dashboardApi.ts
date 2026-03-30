import { httpClient } from '../../../shared/api/httpClient';

// === Types ===
export interface MissionResponse {
  id: number;
  player_id: number;
  date: string;
  text: string;
  point: number;
  status: string;
  sender: string | null;
  msg: string | null;
  proposed_by: string | null;
  proposal_reason: string | null;
  rejection_reason: string | null;
  sort_order: number;
}

export interface CheerResponse {
  id: number;
  date: string;
  sender: string;
  message: string;
}

export interface FeedbackReplyResponse {
  id: number;
  feedback_id: number;
  sender: string;
  text: string;
  created_at: string;
}

export interface FeedbackResponse {
  id: number;
  player_id: number;
  date: string;
  msg: string;
  replies: FeedbackReplyResponse[];
}

export interface DeductionResponse {
  id: number;
  player_id: number;
  date: string;
  reason: string;
  amount: number;
}

export interface DailyPointResponse {
  id: number;
  player_id: number;
  date: string;
  earned: number;
  spent: number;
  balance: number;
}

export interface ConfigResponse {
  id: number;
  key: string;
  value: string | null;
}

export interface PlayerResponse {
  id: number;
  name: string;
  role: string;
  last_login: number | null;
  is_locked: boolean;
}

// === API Functions ===
export const dashboardApi = {
  /** 날짜 변경 시 한번에 병렬 호출 (signal: AbortController.signal for race condition 방지) */
  fetchDayData: async (playerId: number, date: string, signal?: AbortSignal) => {
    const [missions, cheers, feedbacks, deductions, dailyPoint] = await Promise.all([
      httpClient.get<MissionResponse[]>('/api/missions', { params: { player_id: playerId, date }, signal }),
      httpClient.get<CheerResponse[]>('/api/cheers', { params: { date }, signal }),
      httpClient.get<FeedbackResponse[]>('/api/feedbacks', { params: { player_id: playerId, date }, signal }),
      httpClient.get<DeductionResponse[]>('/api/deductions', { params: { player_id: playerId, date }, signal }),
      httpClient.get<DailyPointResponse | null>('/api/daily-points', { params: { player_id: playerId, date }, signal }),
    ]);
    return {
      missions: missions.data,
      cheers: cheers.data,
      feedbacks: feedbacks.data,
      deductions: deductions.data,
      dailyPoint: dailyPoint.data,
    };
  },

  /** 미션 승인 요청 (active → pending_approval) */
  requestApproval: (missionId: number) =>
    httpClient.patch<MissionResponse>(`/api/missions/${missionId}`, { status: 'pending_approval' }),

  /** 미션 제안 */
  proposeMission: (data: {
    player_id: number;
    date: string;
    text: string;
    point: number;
    proposed_by: string;
    proposal_reason?: string;
  }) => httpClient.post<MissionResponse>('/api/missions/propose', data),

  /** 피드백 전송 */
  sendFeedback: (data: { player_id: number; date: string; msg: string }) =>
    httpClient.post<FeedbackResponse>('/api/feedbacks', data),

  /** 전체 플레이어 목록 (랭킹용) */
  getPlayers: () => httpClient.get<PlayerResponse[]>('/api/players'),

  /** 포인트 범위 조회 (랭킹용) */
  getPointsRange: (playerId: number, start: string, end: string) =>
    httpClient.get<DailyPointResponse[]>('/api/daily-points/range', { params: { player_id: playerId, start, end } }),

  /** 앱 설정 조회 (부모 사진, 레벨 임계치 등) */
  getConfig: (key: string) => httpClient.get<ConfigResponse>(`/api/configs/${key}`),

  /** 프로필 상태 메시지 수정 */
  updateStatusMsg: (playerId: number, statusMsg: string) =>
    httpClient.patch(`/api/players/${playerId}`, { status_msg: statusMsg }),
};
