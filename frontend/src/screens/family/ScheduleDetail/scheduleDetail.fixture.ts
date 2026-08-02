import type { ScheduleDetailModel } from './types';
export const scheduleDetailFixture: ScheduleDetailModel = {
  category: '가족 행사',
  title: '가족 저녁 · 삼겹살 파티',
  dateTime: '7월 22일 (수) 오후 7:00',
  place: '집',
  repeat: '매주 반복 안 함',
  attendees: [
    { name: '아빠', tone: 'blue' },
    { name: '엄마', tone: 'red' },
    { name: '서연', tone: 'purple' },
  ],
};
