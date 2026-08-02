import type { ProfileSelectorScreenModel } from './types';

export const profileSelectorFixture: ProfileSelectorScreenModel = {
  brand: '가족 플랫폼',
  tagline: '우리 가족의 공간, 함께 연결되는 하루',
  heading: '사용할 프로필을 선택하세요',
  profiles: [
    { name: '서연', level: 'Lv.3 모험가', points: '1,240P' },
    { name: '민준', level: 'Lv.4 모험가', points: '2,180P' },
    { name: '지호', locked: true, lockReason: '잠김 · 5회 실패', lockRetry: '5분 후 다시 시도할 수 있어요' },
  ],
  lockedNotice: {
    title: '지호의 잠금은 안전을 위한 보호 조치입니다.',
    body: '정상적인 PIN을 입력하면 바로 해제돼요.',
  },
  adminLoginLabel: '관리자 로그인',
};
