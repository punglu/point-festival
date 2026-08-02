export type FamilyInviteAcceptanceModel = {
  familyName: string;
  inviter: string;
  memberCount: string;
  since: string;
  myName: string;
  roles: { label: string; selected: boolean }[];
  notice: string;
};
export type FamilyInviteAcceptanceProps = {
  model: FamilyInviteAcceptanceModel;
  onAccept?: () => void;
  onDecline?: () => void;
};
