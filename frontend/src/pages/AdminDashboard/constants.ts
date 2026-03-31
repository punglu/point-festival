export interface AdminMenuItem {
  key: string;
  label: string;
  path: string;
  icon: string;
  badge?: 'notification';
}

export const ADMIN_MENU_ITEMS: AdminMenuItem[] = [
  { key: 'dashboard',    label: '대시보드',  path: '/admin',              icon: '🏠' },
  { key: 'mission',      label: '미션 관리', path: '/admin/mission',      icon: '⚔️' },
  { key: 'point',        label: '포인트',    path: '/admin/point',        icon: '💎' },
  { key: 'player',       label: '플레이어',  path: '/admin/player',       icon: '👾' },
  { key: 'config',       label: '설정',      path: '/admin/config',       icon: '⚙️' },
  { key: 'notification', label: '알림',      path: '/admin/notification', icon: '🔔', badge: 'notification' },
];
