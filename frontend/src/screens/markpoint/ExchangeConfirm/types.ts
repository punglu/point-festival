export type ExchangeConfirmModel = {
  icon: string;
  rewardName: string;
  note: string;
  currentBalance: number;
  balanceAfter: number;
  cost: number;
};

export type ExchangeConfirmProps = {
  model: ExchangeConfirmModel;
  onCancel?: () => void;
  onConfirm?: () => void;
};
