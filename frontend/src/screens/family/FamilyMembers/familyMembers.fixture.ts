import type { FamilyMembersModel } from './types';

export const familyMembersFixture: FamilyMembersModel = {
  familyName: '우리 가족',
  familyTagline: '함께하는 행복한 하루',
  familyDescription: '가족 구성원은 일정, 앨범, 미션을 함께 확인할 수 있어요.',
  memberSummary: '우리 가족 4명',
  members: [
    { name: '아빠', role: '가족 관리자', letter: '아빠', isGuardian: true },
    { name: '엄마', role: '보호자', letter: '엄마', isGuardian: true },
    { name: '민준', role: '자녀 · Lv.2 탐험가', letter: '민준', isGuardian: false },
    { name: '서연', role: '자녀 · Lv.3 모험가', letter: '서연', isGuardian: false },
  ],
  pendingChildRequestName: '민준',
};
