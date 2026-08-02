import type { CommentComposerModel } from './types';
export const commentComposerFixture: CommentComposerModel = {
  commentCount: 3,
  post: {
    badge: '공지',
    author: '아빠',
    time: '2시간 전',
    title: '이번 주말 가족 나들이 안내',
    body: '토요일 오전 10시에 다 함께 공원에 나가요! 편한 신발을 준비해주세요.',
  },
  comments: [
    { author: '엄마', message: '좋아요! 저는 도시락 준비할게요 🍙', time: '2시간 전' },
    { author: '서연', message: '저 새 운동화 신고 갈래요!', time: '1시간 전' },
    { author: '민준', message: '저도 갈래요 ㅋㅋ 기대돼요', time: '32분 전' },
  ],
  placeholder: '댓글을 입력하세요 (나)',
  myInitial: '서연',
};
