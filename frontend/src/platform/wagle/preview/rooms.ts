import type { WaglePreviewRoom } from './types';

export const waglePreviewRooms: WaglePreviewRoom[] = [
  { id: 'direct', kind: 'DIRECT', name: '엄마', preview: '저녁 먹고 이야기해요', time: '오후 7:42', unread: 2 },
  { id: 'group', kind: 'GROUP', name: '우리 가족 주말 계획', preview: '토요일 오전에 출발하면 어때요?', time: '오후 6:18' },
  { id: 'service', kind: 'SERVICE', name: '마크포인트 알림', preview: '미션 완료 · +25 포인트', time: '오후 4:05', unread: 12 },
  {
    id: 'direct-long',
    kind: 'DIRECT',
    name: '아빠 (긴 표시 이름 줄바꿈 확인용으로 일부러 길게 늘어뜨린 이름)',
    preview: '이번 주말에 다 같이 나가서 저녁을 먹을지 아니면 집에서 시켜 먹을지 아직 못 정해서 이야기가 더 필요할 것 같아요',
    time: '오전 11:03',
  },
];

export const waglePreviewRoomLabels: Record<WaglePreviewRoom['kind'], string> = {
  DIRECT: '개인 대화',
  GROUP: '가족 그룹',
  SERVICE: '서비스 알림',
};
