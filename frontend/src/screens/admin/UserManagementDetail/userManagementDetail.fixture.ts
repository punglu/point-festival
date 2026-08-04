import type { UserManagementDetailModel } from './types';

export const userManagementDetailFixture: UserManagementDetailModel = {
  name: '서연',
  roleLabel: '자녀',
  levelLabel: 'Lv.3 모험가',
  joinedLabel: '2024년 3월 12일',
  lastActiveLabel: '오늘 17:10',
  isActive: true,
  pointsLabel: '320P',
  totalEarnedLabel: '2,480P',
  completedMissionsLabel: '48개',
  redeemCountLabel: '7회',
  pinStatusLabel: '설정됨',
  notificationLabel: '켜짐',
  guardianApprovalLabel: '필요',
  recentMissions: [
    { name: '숙제 다 하기', status: '진행 중' },
    { name: '방 청소하기', status: '완료' },
    { name: '독서 미션', status: '완료' },
  ],
};
