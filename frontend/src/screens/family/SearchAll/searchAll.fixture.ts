import type { SearchAllModel } from './types';
export const searchAllFixture: SearchAllModel = {
  query: '여행',
  cancelLabel: '취소',
  filters: ['전체 8', '미션 1', '대화 2', '앨범 3', '일정 1'],
  activeFilter: '전체 8',
  groups: [
    {
      label: '앨범',
      items: [
        { icon: '▦', iconTone: 'blue', titleParts: [{ hl: '여행' }, ' · 남해'], meta: '앨범 · 24장' },
      ],
    },
    {
      label: '일정',
      items: [
        { icon: '▦', iconTone: 'green', titleParts: ['여름 ', { hl: '여행' }, ' 출발'], meta: '7월 29일 · 온 가족' },
      ],
    },
    {
      label: '대화',
      items: [
        { icon: '아빠', iconTone: 'blue', titleParts: ['아빠님이 가족 앨범 \'', { hl: '여행' }, '\'에 사진을 추가했습니다'], meta: '우리 가족방 · 어제' },
        { icon: '서연', iconTone: 'purple', titleParts: ['이번 ', { hl: '여행' }, ' 진짜 기대돼요!'], meta: '우리 가족방 · 3일 전' },
      ],
    },
    {
      label: '미션',
      items: [
        { icon: '🧳', iconTone: 'purple', titleParts: [{ hl: '여행' }, ' 짐 싸기'], meta: '+30P · 전체' },
      ],
    },
  ],
  recentSearches: ['엄마 생일', '방 청소', '민준'],
};
