import type { ParentDashboardModel } from './types';

export const parentDashboardFixture: ParentDashboardModel = {
  title: '안녕하세요, 관리자님',
  cycleLabel: '08.01 ~ 08.07',
  statCards: [
    { key: 'points', label: '이번 주기 진행률', value: '62%', subtext: '완료 8 / 전체 13' },
    { key: 'active', label: '활성 미션', value: 6, subtext: '오늘 2건' },
    { key: 'pending', label: '승인 대기', value: 4, subtext: '확인 필요', subtextColor: '#D97706' },
    { key: 'completed', label: '이번 주기 완료', value: 8, subtext: '목표 15건' },
  ],
  selectedStatCard: null,
};
