export type RewardExchangeItem = { name: string; meta: string; action: string; icon: string; unavailable?: boolean };

export type RewardExchangeModel = {
  playerName: string;
  balance: number;
  filters: string[];
  activeFilter: string;
  rewards: RewardExchangeItem[];
  historyName: string;
  historyMeta: string;
  historyAmount: string;
};

export type RewardExchangeProps = {
  model: RewardExchangeModel;
  onBack?: () => void;
  onSearch?: () => void;
  onFilter?: (filter: string) => void;
  onSelectReward?: (reward: RewardExchangeItem) => void;
};
