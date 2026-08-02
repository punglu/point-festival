import type { FamilyTodoModel } from './types';

export const familyTodoFixture: FamilyTodoModel = {
  summary: '오늘 6개 · 완료 3개',
  progressPercent: 50,
  progressSubtitle: '3개 남았어요 · 마감 임박 1개',
  counts: [
    { label: '완료', value: '3개' },
    { label: '진행 중', value: '2개' },
    { label: '지연', value: '1개' },
  ],
  filters: ['우리 가족', '서연', '민준', '완료'],
  activeFilter: '우리 가족',
  dateLabel: '7월 22일 (수)',
  todos: [
    { id: 't1', title: '재활용 분리배출', meta: '민준 · 오전 8:00 완료', status: '완료' },
    { id: 't2', title: '방 청소하기', meta: '서연 · 오후 5:10 완료 · +40P', status: '완료' },
    { id: 't3', title: '장보기 · 삼겹살, 상추', meta: '아빠 · 오후 6:30까지', status: '진행 중' },
    { id: 't4', title: '숙제 다 하기', meta: '서연 · 3/5 완료 · +40P', status: '진행 중' },
    { id: 't5', title: '독서록 제출', meta: '민준 · 어제 마감 · 1일 지연', status: '지연' },
  ],
  goals: [
    { title: '함께 저녁 먹기 5회', value: '4/5', percent: 80 },
    { title: '집안일 나눠 하기 12회', value: '9/12', percent: 75 },
  ],
};
