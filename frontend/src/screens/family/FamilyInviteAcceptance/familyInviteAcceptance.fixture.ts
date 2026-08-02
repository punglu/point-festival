import type { FamilyInviteAcceptanceModel } from './types';
export const familyInviteAcceptanceFixture: FamilyInviteAcceptanceModel = {
  familyName: '우리 가족',
  inviter: '엄마',
  memberCount: '구성원 4명 · 2024년 3월부터',
  since: '2024년 3월부터',
  myName: '지호',
  roles: [
    { label: '자녀', selected: true },
    { label: '보호자', selected: false },
  ],
  notice: '참여 후 보호자 승인이 필요할 수 있어요.',
};
