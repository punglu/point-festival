export type FamilyInviteCancelModel = {
  title: string;
  code: string;
  invitee: string;
  issuedAt: string;
  status: string;
  warning: string;
  reasonLabel: string;
  reasonPlaceholder: string;
};
export type FamilyInviteCancelProps = {
  model: FamilyInviteCancelModel;
  onBack?: () => void;
  onConfirm?: (reason: string) => void;
};
