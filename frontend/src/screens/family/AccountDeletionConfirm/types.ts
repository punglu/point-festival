export type AccountDeletionConfirmModel = {
  title: string;
  question: string;
  itemsIntro: string;
  items: string[];
  confirmHint: string;
  confirmWord: string;
};
export type AccountDeletionConfirmProps = {
  model: AccountDeletionConfirmModel;
  onBack?: () => void;
  onConfirm?: (typed: string) => void;
};
