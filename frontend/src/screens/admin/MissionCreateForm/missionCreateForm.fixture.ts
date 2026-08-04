import type { MissionCreateFormModel } from './types';

export const missionCreateFormFixture: MissionCreateFormModel = {
  assignees: [
    { id: 1, name: '서연' },
    { id: 2, name: '민준' },
  ],
  selectedAssigneeIds: [1, 2],
  title: '방 청소하기',
  description: '내 방을 깨끗하게 정리해요',
  point: 40,
  quickPointOptions: [5, 10, 20, 30],
  dateMode: 'today',
  todayLabel: '오늘',
  tomorrowLabel: '내일',
  customDate: '',
  submitting: false,
  canSubmit: true,
  validationMessage: null,
};
