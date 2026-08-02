import type { PopularPostsModel } from './types';
export const popularPostsFixture: PopularPostsModel = {
  title: '인기 게시글',
  subtitle: '공감·댓글이 많은 글이에요',
  ranges: ['이번 주', '이번 달', '전체'],
  activeRange: '이번 주',
  posts: [
    { rank: 1, title: '이번 주말 가족 나들이 안내', author: '아빠', time: '2시간 전', likes: 4, comments: 3 },
    { rank: 2, badge: '자유', title: '오늘 급식 진짜 맛있었어요 😋', author: '서연', time: '2일 전', likes: 3, comments: 0 },
    { rank: 3, badge: '건의', title: '주말엔 게임 시간 늘려주세요!', author: '민준', time: '어제', likes: 2, comments: 1 },
  ],
};
