import { httpClient } from '../../../shared/api/httpClient';
import type {
  Player, Mission, Deduction, DailyPoint,
  Notification, AppConfig, LoginLog, CheerMessage,
  FeedbackItem, FeedbackReplyItem,
} from '../types/admin.types';

interface MissionCloneResponse {
  cloned_count: number;
  missions: Mission[];
}

export const adminApi = {
  // ===== 플레이어 =====
  getPlayers: (signal?: AbortSignal) =>
    httpClient.get<Player[]>('/api/admin/players', { signal }),

  updatePlayer: (id: number, data: Partial<Pick<Player, 'name' | 'status_msg' | 'photo'>>, signal?: AbortSignal) =>
    httpClient.patch<Player>(`/api/admin/players/${id}`, data, { signal }),

  lockPlayer: (id: number, isLocked: boolean, signal?: AbortSignal) =>
    httpClient.patch<Player>(`/api/admin/players/${id}/lock`, { is_locked: isLocked }, { signal }),

  setPlayerVisibility: (id: number, data: { is_dashboard_visible?: boolean }, signal?: AbortSignal) =>
    httpClient.patch<Player>(`/api/admin/players/${id}/visibility`, data, { signal }),

  changePlayerPin: (id: number, pin: string, signal?: AbortSignal) =>
    httpClient.patch(`/api/admin/players/${id}/pin`, { pin }, { signal }),

  createPlayer: (data: { name: string; pin: string; role?: string }, signal?: AbortSignal) =>
    httpClient.post<Player>('/api/players', data, { signal }),

  deletePlayer: (id: number, signal?: AbortSignal) =>
    httpClient.delete(`/api/players/${id}`, { signal }),

  // ===== 미션 =====
  getMissions: (params: { player_id?: number; date?: string; date_from?: string; date_to?: string }, signal?: AbortSignal) =>
    httpClient.get<Mission[]>('/api/admin/missions', { params, signal }),

  createMission: (data: { player_id: number; date: string; text: string; point: number; group_id?: string }, signal?: AbortSignal) =>
    httpClient.post<Mission>('/api/admin/missions', data, { signal }),

  updateMission: (id: number, data: Partial<Pick<Mission, 'text' | 'point' | 'status'> & { msg?: string | null }>, signal?: AbortSignal) =>
    httpClient.patch<Mission>(`/api/admin/missions/${id}`, data, { signal }),

  updateMissionStatus: (id: number, status: string, rejectionReason?: string, signal?: AbortSignal) =>
    httpClient.patch<Mission>(`/api/admin/missions/${id}/status`, { status, rejection_reason: rejectionReason }, { signal }),

  deleteMission: (id: number, signal?: AbortSignal) =>
    httpClient.delete(`/api/admin/missions/${id}`, { signal }),

  deleteMissionGroup: (groupId: string, signal?: AbortSignal) =>
    httpClient.delete(`/api/admin/missions/by-group/${groupId}`, { signal }),

  revertMission: (id: number, signal?: AbortSignal) =>
    httpClient.post<Mission>(`/api/admin/missions/${id}/revert`, {}, { signal }),

  batchCopyMissions: (data: { player_id: number; source_date: string; target_date: string; mission_ids: number[]; point_overrides?: Record<number, number> }, signal?: AbortSignal) =>
    httpClient.post<Mission[]>('/api/admin/missions/clone-selected', data, { signal }),

  cloneMissions: (data: { source_player_id: number; source_date: string; target_date: string; point_overrides?: Record<number, number> }, signal?: AbortSignal) =>
    httpClient.post<MissionCloneResponse>('/api/admin/missions/clone', data, { signal }),

  // ===== 차감 =====
  getDeductions: (params: { player_id?: number; date?: string }, signal?: AbortSignal) =>
    httpClient.get<Deduction[]>('/api/admin/deductions', { params, signal }),

  createDeduction: (data: { player_id: number; date: string; reason: string; amount: number }, signal?: AbortSignal) =>
    httpClient.post<Deduction>('/api/admin/deductions', data, { signal }),

  updateDeduction: (id: number, data: Partial<Pick<Deduction, 'reason' | 'amount'>>, signal?: AbortSignal) =>
    httpClient.patch<Deduction>(`/api/admin/deductions/${id}`, data, { signal }),

  deleteDeduction: (id: number, signal?: AbortSignal) =>
    httpClient.delete(`/api/admin/deductions/${id}`, { signal }),

  // ===== 포인트 =====
  getDailyPoints: (params: { player_id?: number; date?: string }, signal?: AbortSignal) =>
    httpClient.get<DailyPoint[]>('/api/admin/daily-points', { params, signal }),

  getDailyPointsRange: (playerId: number, start: string, end: string, signal?: AbortSignal) =>
    httpClient.get<DailyPoint[]>('/api/admin/daily-points/range', { params: { player_id: playerId, start, end }, signal }),

  adjustDailyPoint: (data: { player_id: number; date: string; delta: number }, signal?: AbortSignal) =>
    httpClient.post<DailyPoint>('/api/admin/daily-points/adjust', data, { signal }),

  // ===== 알림 =====
  getNotifications: (signal?: AbortSignal) =>
    httpClient.get<Notification[]>('/api/admin/notifications', { signal }),

  createNotification: (data: { player_id?: number; title: string; body?: string; type?: string }, signal?: AbortSignal) =>
    httpClient.post<Notification>('/api/admin/notifications', { type: 'admin', ...data }, { signal }),

  markAsRead: (id: number, signal?: AbortSignal) =>
    httpClient.patch(`/api/admin/notifications/${id}/read`, {}, { signal }),

  markAllAsRead: (signal?: AbortSignal) =>
    httpClient.patch('/api/admin/notifications/read-all', {}, { signal }),

  // ===== 설정 =====
  getConfig: (key: string, signal?: AbortSignal) =>
    httpClient.get<AppConfig>(`/api/configs/${key}`, { signal }),

  updateConfig: (key: string, value: string, signal?: AbortSignal) =>
    httpClient.put<AppConfig>(`/api/admin/configs/${key}`, { value }, { signal }),

  // ===== 응원 메시지 =====
  getCheers: (date: string, signal?: AbortSignal) =>
    httpClient.get<CheerMessage[]>('/api/cheers', { params: { date }, signal }),

  upsertCheer: (date: string, data: { date: string; sender: string; message: string }, signal?: AbortSignal) =>
    httpClient.put(`/api/admin/cheers/${date}`, data, { signal }),

  // ===== 가족 채팅 (피드백) =====
  getFeedbacks: (date: string, playerId?: number, signal?: AbortSignal) =>
    httpClient.get<FeedbackItem[]>('/api/feedbacks/', {
      params: playerId ? { date, player_id: playerId } : { date },
      signal,
    }),

  sendAdminReply: (data: { feedback_id: number; sender: string; text: string }, signal?: AbortSignal) =>
    httpClient.post<FeedbackReplyItem>('/api/feedbacks/replies', data, { signal }),

  // ===== 로그인 로그 =====
  getLoginLogs: (params?: { player_id?: number; limit?: number }, signal?: AbortSignal) =>
    httpClient.get<LoginLog[]>('/api/admin/login-logs', { params, signal }),
};
