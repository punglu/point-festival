import type { ChatReplyModel } from './types';

export const chatReplyFixture: ChatReplyModel = {
  roomTitle: '우리 가족방',
  backgroundMessages: [
    { tone: 'in', text: '좋지! 나는 김치찌개 끓일게 😊' },
    { tone: 'out', text: '저는 밥할게요 🍚' },
  ],
  quotedAuthor: '엄마',
  quotedText: '좋지! 나는 김치찌개 끓일게 😊\n민준이는 상추 씻는 거 부탁해~',
  draftText: '네, 바로 씻을게요!',
};
