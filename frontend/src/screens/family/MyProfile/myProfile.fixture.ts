import type { MyProfileModel } from './types';

export const myProfileFixture: MyProfileModel = {
  avatarInitial: '서',
  playerName: '서연',
  levelLabel: 'Lv.3 모험가',
  familyMeta: '우리 가족방 · 2024년 3월부터 함께',
  stats: [
    { name: '보유 포인트', value: '320P' },
    { name: '누적 미션', value: '48개' },
    { name: '연속 달성', value: '6일' },
  ],
  levelProgressLabel: '320P / 500P',
  levelProgressPercent: 64,
  levelHint: '180P를 더 모으면 Lv.4 모험가가 돼요.',
  activity: [
    { key: 'points', name: '포인트 내역', value: '이번 달 +240P', icon: 'list' },
    { key: 'missions', name: '완료한 미션', value: '48개', icon: 'check' },
    { key: 'badges', name: '받은 배지', value: '7개', icon: 'star' },
  ],
  settings: [
    { key: 'notifications', name: '알림 설정', value: 'toggle', icon: 'bell' },
    { key: 'pin', name: 'PIN 변경', value: 'lock', icon: 'lock' },
    { key: 'members', name: '가족 구성원', value: '4명', icon: 'people' },
  ],
};
