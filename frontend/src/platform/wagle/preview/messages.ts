import type { WaglePreviewMessage } from './types';

// sender는 GROUP room 렌더링에서만 사용된다(WagleLanding.tsx Conversation) — DIRECT는
// 데이터에 값이 있어도 화면에 표시하지 않는다(상대가 하나뿐이라 헤더 Avatar로 충분).
const standardConversation: WaglePreviewMessage[] = [
  { id: 'standard-1', direction: 'incoming', text: '안녕하세요! 오늘은 어땠어요?', timestamp: '오후 7:38', readState: 'read', sender: { name: '엄마' } },
  { id: 'standard-2', direction: 'outgoing', text: '좋았어요. 조금 뒤에 이야기해요.', timestamp: '오후 7:40', readState: 'read' },
];

// rooms.ts의 direct room(unread: 2)과 맞춰, 마지막 2건을 아직 읽지 않은 수신
// 메시지로 구성한다. UnreadDivider 배치는 WagleLanding에서 room.unread 개수만큼
// 마지막 incoming 메시지 앞에 계산해 표시한다(fixture에 별도 marker 필드 없음).
const directConversation: WaglePreviewMessage[] = [
  ...standardConversation,
  { id: 'direct-3', direction: 'incoming', text: '오늘 저녁 메뉴는 뭐가 좋을까요?', timestamp: '오후 7:41', readState: 'sent' },
  { id: 'direct-4', direction: 'incoming', text: '집에 오는 길에 미리 알려주면 준비해둘게요.', timestamp: '오후 7:42', readState: 'sent' },
];

export const waglePreviewMessagesByRoom: Record<string, WaglePreviewMessage[]> = {
  direct: directConversation,
  group: standardConversation,
  'direct-long': [
    ...standardConversation,
    {
      id: 'direct-long-3',
      direction: 'incoming',
      text: '이번 주말에 다 같이 나가서 저녁을 먹을지, 아니면 집에서 시켜 먹을지 아직 정하지 못해서 이야기가 더 필요할 것 같아요. 시간 괜찮을 때 편하게 답해주세요.',
      timestamp: '오전 11:05',
      readState: 'read',
    },
  ],
};

export const waglePreviewDefaultConversation = standardConversation;
