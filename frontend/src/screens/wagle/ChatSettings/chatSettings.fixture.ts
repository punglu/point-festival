import type { ChatSettingsModel } from './types';

export const chatSettingsFixture: ChatSettingsModel = {
  roomName: '우리 가족방',
  memberSummary: '4명 참여 중',
  items: [
    { name: '알림', description: '새 메시지 알림', hasToggle: true },
    { name: '사진 및 미디어', description: '사진 저장 설정' },
    { name: '대화 내용 내보내기', description: '채팅 기록을 파일로 저장' },
  ],
  members: [{ name: '아빠' }, { name: '엄마' }, { name: '민준' }, { name: '서연' }],
};
