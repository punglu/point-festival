import type { ScheduleAddModel } from './types';

export const scheduleAddFixture: ScheduleAddModel = {
  title: '가족 저녁 · 삼겹살 파티',
  date: '2026년 7월 22일',
  time: '오후 7:00',
  place: '집',
  attendees: [
    { name: '아빠', selected: true },
    { name: '엄마', selected: true },
    { name: '민준', selected: true },
    { name: '서연', selected: true },
  ],
  reminder: '10분 전',
  memo: '맛있는 저녁을 함께 먹어요!',
};
