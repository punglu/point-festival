import type { MissionManagementModel } from './types';

export const missionManagementFixture: MissionManagementModel = {
  stats: [
    { label: '전체 미션', value: '12개' },
    { label: '진행 중', value: '8개' },
    { label: '승인 대기', value: '4개' },
  ],
  playerOptions: [
    { id: 1, name: '서연' },
    { id: 2, name: '민준' },
  ],
  selectedPlayerId: null,
  selectedDate: '2026-08-05',
  filterStatus: 'all',
  searchQuery: '',
  rows: [
    { id: 1, content: '숙제 다 하기 · 매일 · +40P · 진행 중' },
    { id: 2, content: '방 청소하기 · 매주 토요일 · +40P · 진행 중' },
    { id: 3, content: '독서 미션 · 매일 · +30P · 활성' },
    { id: 4, content: '동생과 사이좋게 지내기 · 매일 · +40P · 활성' },
  ],
  canBulkApprove: false,
  loading: false,
};
