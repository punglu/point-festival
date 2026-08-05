import type { PointFestivalScreenModel } from './types';

export const pointFestivalFixture: PointFestivalScreenModel = {
  playerName: '서연',
  level: 3,
  levelProgressPercent: 64,
  earnedLabel: '320P / 500P',
  levelHint: '다음 레벨까지 180P 남았어요',
  todayEarned: 40,
  remainingMissions: 2,
  currentBalance: 320,
  weekLabel: '7월 3주차 ›',
  selectedDate: '22',
  days: [
    { weekday: '월', day: '20', date: '20' },
    { weekday: '화', day: '21', date: '21' },
    { weekday: '수', day: '22', date: '22' },
    { weekday: '목', day: '23', date: '23' },
    { weekday: '금', day: '24', date: '24' },
    { weekday: '토', day: '25', date: '25' },
    { weekday: '일', day: '26', date: '26' },
  ],
  cheerMessages: [
    { name: '엄마', tone: 'mom', message: '서연아, 오늘도 힘내!\n너라면 잘할 수 있어 💜', time: '1시간 전' },
    { name: '아빠', tone: 'dad', message: '미션 하나씩 해내는 모습이\n정말 멋져요! 👍', time: '3시간 전' },
  ],
  missionsTitle: '오늘의 미션',
  missions: [
    { id: 1, title: '방 청소하기', subtitle: '내 방을 깨끗하게 정리해요', reward: '+40P', status: '완료', statusKind: 'complete', progress: '100%', count: '1/1' },
    { id: 2, title: '숙제 다 하기', subtitle: '오늘의 숙제를 모두 완료해요', reward: '+40P', status: '진행 중', statusKind: 'progress', action: '바로가기', progress: '60%', count: '3/5' },
    { id: 3, title: '동생과 사이좋게', subtitle: '동생에게 친절하게 대해요', reward: '+40P', status: '승인 대기', statusKind: 'pending', action: '바로가기', progress: '0%', count: '0/1' },
  ],
  historyEntry: { title: '포인트 사용 내역', subtitle: '문구점에서 노트 구입', amount: '−30P', time: '어제 17:30' },
};
