export type ChildInviteModel = {
  childName: string;
  headline: string;
  description: string;
  letter: string;
  detail: string;
};

export type ChildInviteProps = {
  model: ChildInviteModel;
  onApprove?: () => void;
  onDismiss?: () => void;
};
