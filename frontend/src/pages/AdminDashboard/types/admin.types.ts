// ===== 플레이어 =====
export interface Player {
  id: number;
  name: string;
  role: string;
  status_msg: string | null;
  photo: string | null;
  last_login: number | null;
  is_locked: boolean;
}

// ===== 미션 =====
export type MissionStatus =
  | 'active'
  | 'pending_approval'
  | 'completed'
  | 'failed'
  | 'rejected'
  | 'proposed';

export interface Mission {
  id: number;
  player_id: number;
  date: string;
  text: string;
  point: number;
  status: MissionStatus;
  sender: string | null;
  proposed_by: string | null;
  proposal_reason: string | null;
  rejection_reason: string | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

// ===== 차감 =====
export interface Deduction {
  id: number;
  player_id: number;
  date: string;
  reason: string;
  amount: number;
  created_at: string;
}

// ===== 포인트 =====
export interface DailyPoint {
  id: number;
  player_id: number;
  date: string;
  earned: number;
  spent: number;
  balance: number;
}

// ===== 알림 =====
export type NotificationType =
  | 'approval_request'
  | 'proposal'
  | 'system'
  | 'level_up'
  | 'cycle_reset';

export interface Notification {
  id: number;
  type: NotificationType;
  player_id: number | null;
  title: string;
  body: string | null;
  is_read: boolean;
  created_at: string;
}

// ===== 설정 =====
export interface AppConfig {
  id: number;
  key: string;
  value: string | null;
}

// ===== 응원 메시지 =====
export interface CheerMessage {
  id: number;
  date: string;
  sender: string;
  message: string;
}

// ===== 로그인 로그 =====
export interface LoginLog {
  id: number;
  player_id: number;
  success: boolean;
  date: string;
  created_at: string;
}

// ===== 대시보드 집계 =====
export interface DashboardStats {
  totalActiveMissions: number;
  pendingApproval: number;
  completedThisWeek: number;
  totalPointsIssued: number;
  todayNewMissions: number;
  weeklyGoal: number;
}

export interface MissionRankItem {
  text: string;
  totalCount: number;
  playerCounts: Record<string, number>;
}

// ===== 가족 채팅 (피드백) =====
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
  player_name?: string;
  replies: FeedbackReplyItem[];
}

// ===== 사이드바 메뉴 =====
export interface SidebarMenuItem {
  key: string;
  label: string;
  path: string;
  icon: string;
  group: 'main' | 'manage';
  badge?: number;
}
