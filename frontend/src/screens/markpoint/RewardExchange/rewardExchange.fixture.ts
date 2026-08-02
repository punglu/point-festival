import type { RewardExchangeModel } from './types';

export const rewardExchangeFixture: RewardExchangeModel = {
  playerName: '서연',
  balance: 320,
  filters: ['전체', '간식', '장난감', '특별 외출'],
  activeFilter: '전체',
  rewards: [
    { name: '편의점 젤리 교환권', meta: '문구점/편의점에서 사용', action: '30P 교환', icon: '♧' },
    { name: '게임 30분 추가', meta: '주말에만 사용 가능', action: '80P 교환', icon: '◷' },
    { name: '가족 영화관 나들이', meta: '원하는 영화 함께 보기', action: '300P 필요', icon: '▣', unavailable: true },
    { name: '캐릭터 노트 세트', meta: '문구점에서 즉시 수령', action: '50P 교환', icon: '✎' },
  ],
  historyName: '젤리 간식 교환',
  historyMeta: '어제 17:30 · 승인 완료',
  historyAmount: '−30P',
};
