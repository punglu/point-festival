import { httpClient } from '../../../shared/api/httpClient';

// === Types ===
export interface MissionItem {
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

export interface MissionCloneRequest {
  source_player_id: number;
  source_date: string;
  target_date: string;
  point_overrides?: Record<number, number> | null;
}

export interface MissionCloneResponse {
  cloned_count: number;
  missions: MissionItem[];
}

export interface DeductionItem {
  id: number;
  player_id: number;
  date: string;
  reason: string;
  amount: number;
}

export interface DailyPointItem {
  id: number;
  player_id: number;
  date: string;
  earned: number;
  spent: number;
  balance: number;
}

export interface CheerItem {
  id: number;
  date: string;
  sender: string;
  message: string;
}

export interface PlayerItem {
  id: number;
  name: string;
  role: string;
  last_login: number | null;
  is_locked: boolean;
}

export interface NotificationItem {
  id: number;
  type: string;
  player_id: number | null;
  title: string;
  body: string | null;
  is_read: boolean;
  created_at: string;
}

export interface FeedbackReplyItem {
  id: number;
  feedback_id: number;
  sender: string;
  text: string;
  created_at: string;
}

export interface FeedbackItem {
  id: number;
  player_id: number;
  date: string;
  msg: string;
  replies: FeedbackReplyItem[];
}

export interface ConfigItem {
  id: number;
  key: string;
  value: string | null;
}

// === API Functions ===
export const adminApi = {
  // ─── 미션 ────────────────────────────────────────────────
  createMission: (data: Omit<MissionItem, 'id' | 'proposed_by' | 'proposal_reason' | 'rejection_reason'>, signal?: AbortSignal) =>
    httpClient.post<MissionItem>('/api/admin/missions', data, { signal }),

  updateMission: (id: number, data: Partial<MissionItem>, signal?: AbortSignal) =>
    httpClient.patch<MissionItem>(`/api/admin/missions/${id}`, data, { signal }),

  deleteMission: (id: number, signal?: AbortSignal) =>
    httpClient.delete(`/api/admin/missions/${id}`, { signal }),

  cloneMissions: (data: MissionCloneRequest, signal?: AbortSignal) =>
    httpClient.post<MissionCloneResponse>('/api/admin/missions/clone', data, { signal }),

  // ─── 포인트 ──────────────────────────────────────────────
  createDeduction: (data: Omit<DeductionItem, 'id'>, signal?: AbortSignal) =>
    httpClient.post<DeductionItem>('/api/admin/deductions', data, { signal }),

  adjustDailyPoint: (data: { player_id: number; date: string; earned_delta: number; spent_delta: number }, signal?: AbortSignal) =>
    httpClient.post<DailyPointItem>('/api/admin/daily-points/adjust', data, { signal }),

  // ─── 응원 ────────────────────────────────────────────────
  upsertCheer: (date: string, data: { date: string; sender: string; message: string }, signal?: AbortSignal) =>
    httpClient.put<CheerItem>(`/api/admin/cheers/${date}`, data, { signal }),

  // ─── 플레이어 ─────────────────────────────────────────────
  updatePlayer: (id: number, data: { name?: string; status_msg?: string; photo?: string }, signal?: AbortSignal) =>
    httpClient.patch<PlayerItem>(`/api/admin/players/${id}`, data, { signal }),

  lockPlayer: (id: number, isLocked: boolean, signal?: AbortSignal) =>
    httpClient.patch<PlayerItem>(`/api/admin/players/${id}/lock`, { is_locked: isLocked }, { signal }),

  // ─── 알림 ────────────────────────────────────────────────
  getNotifications: (signal?: AbortSignal) =>
    httpClient.get<NotificationItem[]>('/api/admin/notifications', { signal }),

  createNotification: (data: { type: string; player_id?: number; title: string; body?: string }, signal?: AbortSignal) =>
    httpClient.post<NotificationItem>('/api/admin/notifications', data, { signal }),

  markNotificationRead: (id: number, signal?: AbortSignal) =>
    httpClient.patch(`/api/admin/notifications/${id}/read`, {}, { signal }),

  // ─── 피드백 ──────────────────────────────────────────────
  getFeedbacks: (playerId: number, date: string, signal?: AbortSignal) =>
    httpClient.get<FeedbackItem[]>('/api/admin/feedbacks', { params: { player_id: playerId, target_date: date }, signal }),

  createReply: (feedbackId: number, data: { feedback_id: number; sender: string; text: string }, signal?: AbortSignal) =>
    httpClient.post<FeedbackReplyItem>(`/api/admin/feedbacks/${feedbackId}/replies`, data, { signal }),

  // ─── 설정 ────────────────────────────────────────────────
  getConfigs: (signal?: AbortSignal) =>
    httpClient.get<ConfigItem[]>('/api/admin/configs', { signal }),

  updateConfig: (key: string, value: string | null, signal?: AbortSignal) =>
    httpClient.put<ConfigItem>(`/api/admin/configs/${key}`, { value }, { signal }),
};
