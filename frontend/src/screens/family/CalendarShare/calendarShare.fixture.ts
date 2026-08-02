import type { CalendarShareModel } from './types';
export const calendarShareFixture: CalendarShareModel = {
  title: '캘린더 공유',
  subscriptionLink: 'webcal://ourfamily.app/cal/7F3K92.ics',
  copyLabel: '복사',
  integrations: [
    { name: 'Google 캘린더', on: true },
    { name: 'Apple 캘린더', on: false },
  ],
  targets: [
    { name: '아빠', shared: true },
    { name: '엄마', shared: true },
  ],
  confirmLabel: '완료',
};
