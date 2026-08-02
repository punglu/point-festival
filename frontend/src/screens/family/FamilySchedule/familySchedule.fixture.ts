import type { FamilyScheduleModel } from './types';

const days = ['29', '30', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '1', '2'];
const markers: Record<string, string> = { '2': 'purple', '7': 'green', '10': 'purple', '15': 'yellow', '18': 'purple', '21': 'green', '22': 'active', '23': 'purple', '25': 'yellow', '29': 'purple' };

export const familyScheduleFixture: FamilyScheduleModel = {
  weekSummary: '이번 주 일정 5개 · 오늘 2개',
  monthLabel: '2026년 7월',
  weekdays: ['월', '화', '수', '목', '금', '토', '일'],
  days: days.map((day, index) => ({ day, marker: markers[`${day}-${index}`] ?? markers[day] ?? 'empty' })),
  todayLabel: '7월 22일 (수) 일정',
  todayEvents: [
    { id: 'e1', color: 'purple', title: '가족 저녁 · 삼겹살 파티', meta: '오후 7:00 · 집 · 온 가족', people: ['아빠', '엄마', '서연'] },
    { id: 'e2', color: 'green', title: '민준 수학 학원', meta: '오후 4:30 ~ 6:00 · 민준', people: ['민준'] },
  ],
  upcomingEvents: [
    { id: 'e3', color: 'purple', title: '서연 학교 상담', meta: '오전 10:00 · 엄마 참석', people: ['엄마'] },
    { id: 'e4', color: 'yellow', title: '엄마 생일', meta: '7월 25일 (토) · 온 가족', people: ['엄마'] },
    { id: 'e5', color: 'purple', title: '여름 여행 출발', meta: '오전 8:00 · 온 가족 · 2박 3일', people: ['아빠', '엄마', '서연', '민준'] },
  ],
};
