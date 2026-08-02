import type { FamilyBoardModel } from './types';
export const familyBoardFixture: FamilyBoardModel = {
  subtitle: '공지 · 건의 · 자유글을 남겨보세요',
  tabs: ['전체', '공지', '건의', '자유'],
  activeTab: '전체',
  posts: [
    { badge: '공지', badgeTone: 'blue', author: '아빠', time: '2시간 전', title: '이번 주말 가족 나들이 안내', summary: '토요일 오전 10시에 다 함께 공원에 나가요! 편한 신발을 준비해주세요.', likes: 4, comments: 3 },
    { badge: '건의', badgeTone: 'yellow', author: '민준', time: '어제', title: '주말엔 게임 시간 늘려주세요!', summary: '숙제 다 끝내면 주말에는 1시간으로 늘려줄 수 있나요?', likes: 2, comments: 1 },
    { badge: '자유', badgeTone: 'green', author: '서연', time: '2일 전', title: '오늘 급식 진짜 맛있었어요 😋', summary: '', likes: 3, comments: 0 },
  ],
};
