import type { FamilyRulesModel } from './types';

export const familyRulesFixture: FamilyRulesModel = {
  heroTitle: '우리 가족의 약속',
  heroBody: '가족 모두가 편안하고 즐거운 생활을 위해 함께 정한 규칙이에요.',
  lifeRulesLabel: '생활 규칙',
  lifeRules: [
    { name: '저녁 식사 시간', value: '오후 7:00' },
    { name: '하루 미디어 사용', value: '1시간 30분' },
    { name: '취침 시간', value: '오후 10:00' },
    { name: '주말 외출', value: '보호자와 상의 후' },
  ],
  pointRulesLabel: '포인트 규칙',
  pointRules: [
    { name: '미션 완료 포인트', value: '보호자 승인 후 지급' },
    { name: '보상 교환', value: '보호자 승인 필요' },
  ],
};
