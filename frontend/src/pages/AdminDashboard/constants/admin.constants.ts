import type { SidebarMenuItem } from '../types/admin.types';

export const ADMIN_MENU: SidebarMenuItem[] = [
  { key: 'dashboard',      label: '대시보드',      path: '/admin',               icon: 'dashboard',      group: 'main' },
  { key: 'missions',       label: '미션 관리',      path: '/admin/missions',      icon: 'missions',       group: 'main' },
  { key: 'points',         label: '포인트 관리',    path: '/admin/points',        icon: 'points',         group: 'main' },
  { key: 'chat',           label: '가족 채팅',      path: '/admin/chat',          icon: 'chat',           group: 'main'   },
  { key: 'players',        label: '플레이어 관리',  path: '/admin/players',       icon: 'players',        group: 'manage' },
  { key: 'notifications',  label: '알림',           path: '/admin/notifications', icon: 'notifications',  group: 'manage' },
  { key: 'config',         label: '설정',           path: '/admin/config',        icon: 'config',         group: 'manage' },
];

export const COLORS = {
  primary:          '#4338CA',
  primaryLight:     '#818CF8',
  primaryBg:        '#EEF2FF',
  sidebarBg:        '#312E81',
  sidebarText:      '#A5B4FC',
  sidebarTextActive:'#E0E7FF',
  sidebarAccent:    '#A5B4FC',
  success:          '#059669',
  successBg:        '#D1FAE5',
  warning:          '#D97706',
  warningBg:        '#FFFBEB',
  warningText:      '#92400E',
  danger:           '#DC2626',
  dangerBg:         '#FEF2F2',
  contentBg:        '#F8FAFC',
} as const;

export const POINT_QUICK_VALUES = [5, 10, 20, 30] as const;

export const MISSION_STATUS_MAP: Record<string, { label: string; color: string; bgColor: string }> = {
  active:           { label: '도전 중!',        color: '#4338CA', bgColor: '#EEF2FF' },
  pending_approval: { label: '확인 중...',       color: '#92400E', bgColor: '#FEF3C7' },
  completed:        { label: '완료!',            color: '#065F46', bgColor: '#D1FAE5' },
  failed:           { label: '다음에 도전!',     color: '#DC2626', bgColor: '#FEF2F2' },
  rejected:         { label: '다시 생각해보자',  color: '#6B7280', bgColor: '#F3F4F6' },
  proposed:         { label: '제안됨',           color: '#D97706', bgColor: '#FEF3C7' },
};

export const LEVEL_THRESHOLDS = [0, 50, 100, 200, 350, 500] as const;

export const PLAYER_COLORS = ['#4338CA', '#DB2777', '#059669', '#D97706'] as const;
