import type { RewardShopModel } from './types';

export const rewardShopFixture: RewardShopModel = {
  playerInitial: '서',
  balance: 320,
  filters: ['전체', '간식', '놀이', '특별 외출'],
  activeFilter: '전체',
  rewards: [
    { name: '젤리 교환권', icon: '🍬', cost: 30, available: true },
    { name: '캐릭터 노트', icon: '📓', cost: 50, available: true },
    { name: '게임 30분', icon: '🎮', cost: 80, available: true },
    { name: '영화관 나들이', icon: '🎬', cost: 300, available: false },
  ],
  historyName: '젤리 간식 교환',
  historyMeta: '어제 · 승인 완료',
  historyAmount: '−30P',
};
