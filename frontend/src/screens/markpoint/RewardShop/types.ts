export type RewardShopItem = { name: string; icon: string; cost: number; available: boolean };

export type RewardShopModel = {
  playerInitial: string;
  balance: number;
  filters: string[];
  activeFilter: string;
  rewards: RewardShopItem[];
  historyName: string;
  historyMeta: string;
  historyAmount: string;
};

export type RewardShopProps = {
  model: RewardShopModel;
  onFilter?: (filter: string) => void;
  onSelectReward?: (reward: RewardShopItem) => void;
};
