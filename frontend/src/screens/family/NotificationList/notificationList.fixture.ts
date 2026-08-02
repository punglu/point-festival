import type { NotificationListModel } from './types';

export const notificationListFixture: NotificationListModel = {
  unreadCount: 3,
  filters: ['전체', '새 알림', '포인트', '일정', '앨범'],
  activeFilter: '전체',
  todayLabel: '오늘',
  notifications: [
    { icon: '★', title: '미션 완료를 축하해요!', text: '서연이가 "숙제 다 하기"를 완료했어요. +40P', time: '12분 전', unread: true },
    { icon: 'P', title: '포인트가 지급되었어요', text: '보호자 승인으로 40P가 지급되었어요.', time: '1시간 전', unread: true },
    { icon: '▣', title: '가족 일정 알림', text: '오늘 저녁 7시, 가족 저녁 · 삼겹살 파티가 있어요.', time: '2시간 전', unread: true },
    { icon: '▧', title: '새 사진이 추가됐어요', text: '아빠가 가족 앨범에 사진 3장을 추가했어요.', time: '오후 6:35', unread: false },
    { icon: '!', title: '미션 마감이 다가와요', text: '독서록 제출 미션이 오늘 마감돼요.', time: '어제', unread: false },
  ],
  footerNote: '알림 설정은 나 · 프로필에서 변경할 수 있어요.',
};
