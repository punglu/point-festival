import type { MissionDetailModel } from './types';

export const missionDetailFixture: MissionDetailModel = {
  title: '숙제 다 하기',
  description: '오늘의 숙제를 모두 완료해요',
  reward: '+40P',
  progressPercent: 60,
  completedCount: 3,
  totalCount: 5,
  checklist: [
    { label: '수학 익힘책 12쪽', done: true },
    { label: '영어 단어 20개 쓰기', done: true },
    { label: '일기 쓰기', done: true },
    { label: '독서록 작성', done: false },
    { label: '준비물 챙기기', done: false },
  ],
  photoNotice: '완료한 모습을 사진으로 남기면 보호자가 빠르게 확인할 수 있어요.',
  submitNotice: '제출하면 보호자 승인 후 포인트가 지급돼요.',
};
