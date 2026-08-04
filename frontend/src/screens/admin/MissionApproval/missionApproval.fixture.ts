import type { MissionApprovalModel } from './types';

export const missionApprovalFixture: MissionApprovalModel = {
  pendingCount: 4,
  approvedTodayCount: 6,
  rejectedTodayCount: 1,
  pendingPoints: 150,
  items: [
    { id: 1, playerName: '서연', title: '방 청소하기', meta: '오늘 17:10 제출 · +40P' },
    { id: 2, playerName: '민준', title: '동생과 사이좋게 지내기', meta: '오늘 16:40 제출 · +40P' },
    { id: 3, playerName: '서연', title: '숙제 다 하기 · 독서록', meta: '오늘 15:52 제출 · +40P' },
    { id: 4, playerName: '민준', title: '재활용 분리배출', meta: '오늘 8:05 제출 · +30P' },
  ],
};
