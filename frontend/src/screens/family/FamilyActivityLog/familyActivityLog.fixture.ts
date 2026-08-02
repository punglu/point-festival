import type { FamilyActivityLogModel } from './types';
export const familyActivityLogFixture: FamilyActivityLogModel = {
  title: '가족 활동 로그',
  filters: ['전체', '서연', '민준', '부모'],
  activeFilter: '전체',
  days: [
    {
      label: '오늘',
      events: [
        { initial: '서연', tone: 'purple', title: '방 청소하기 완료', detail: '+40P 지급', time: '17:10' },
        { initial: '아빠', tone: 'blue', title: '젤리 간식 교환 승인', detail: '−30P · 서연', time: '17:32' },
        { initial: '민준', tone: 'green', title: '재활용 분리배출 제출', detail: '승인 대기 중', time: '08:05' },
      ],
    },
    {
      label: '어제',
      events: [
        { initial: '★', tone: 'yellow', title: '서연이 Lv.3 모험가 달성', time: '18:40' },
        { initial: '엄마', tone: 'red', title: '민준에게 약속 시간 지연 차감', detail: '−10P', time: '16:20' },
      ],
    },
  ],
};
