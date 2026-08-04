import type { FamilyChatModel } from './types';

export const familyChatFixture: FamilyChatModel = {
  roomTitle: '우리 가족방',
  participants: [
    { id: 'dad', name: '아빠' },
    { id: 'mom', name: '엄마' },
    { id: 'minjun', name: '민준' },
    { id: 'seoyeon', name: '서연' },
  ],
  connectionState: 'connected',
  connectionLabel: '실시간 연결됨',
  draft: '',
  sending: false,
  sendError: null,
  replyBannerText: null,
  messages: [
    { id: '1', kind: 'other', authorName: '아빠', body: '오늘 저녁은 삼겹살 어때?\n장도 보고 올게!', deleted: false, time: '오후 6:01' },
    { id: '2', kind: 'other', authorName: '엄마', body: '좋지! 나는 김치찌개 끓일게 😊\n민준이는 상추 씻는 거 부탁해~', deleted: false, time: '오후 6:02' },
    { id: '3', kind: 'other', authorName: '민준', body: '네! 알겠어요 👍', deleted: false, time: '오후 6:03' },
    { id: '4', kind: 'own', body: '저는 밥할게요 🍚\n오늘도 맛있는 저녁 기대돼요!', deleted: false, time: '오후 6:04' },
    { id: '5', kind: 'other', authorName: '아빠', body: '우리 딸 든든하다~ 고마워!', deleted: false, time: '오후 6:04' },
    { id: '6', kind: 'other', authorName: '엄마', body: '민준아, 방 청소는 다 했지? 😊', deleted: false, time: '오후 6:20' },
    { id: '7', kind: 'other', authorName: '민준', body: '방금 끝냈어요 ✨', deleted: false, time: '오후 6:21' },
  ],
};
