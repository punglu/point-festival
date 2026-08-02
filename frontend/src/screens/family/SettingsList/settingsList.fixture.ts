import type { SettingsListModel } from './types';

export const settingsListFixture: SettingsListModel = {
  playerInitial: '서',
  playerName: '서연',
  playerMeta: 'Lv.3 모험가 · 프로필 관리',
  navGroups: [
    {
      title: '계정',
      items: [
        { key: 'pin', label: 'PIN 변경', icon: '🔒' },
        { key: 'members', label: '가족 구성원', icon: '👪', detail: '4명' },
        { key: 'delete-account', label: '계정 탈퇴', icon: '⚠' },
      ],
    },
    {
      title: '표시',
      items: [
        { key: 'notification-detail', label: '알림 세부설정', icon: '🔔' },
        { key: 'language', label: '언어', icon: '🌐', detail: '한국어' },
        { key: 'theme', label: '화면 테마', icon: '☀' },
        { key: 'widgets', label: '위젯 관리', icon: '▦' },
      ],
    },
    {
      title: '지원',
      items: [
        { key: 'help', label: '도움말 · 문의하기', icon: '❓' },
        { key: 'terms', label: '이용약관 · 개인정보처리방침', icon: '📄' },
      ],
    },
  ],
  toggleGroups: [
    {
      title: '알림',
      items: [
        { key: 'push', label: '푸시 알림', icon: '🔔', on: true },
        { key: 'chat', label: '가족 대화 알림', icon: '📍', on: true },
      ],
    },
    {
      title: '화면',
      items: [
        { key: 'dark-mode', label: '다크 모드', icon: '☀', on: false },
        { key: 'large-text', label: '큰 글씨 모드', icon: '≡', on: false },
      ],
    },
  ],
  version: 'v1.0.0 · 가족 플랫폼',
};
