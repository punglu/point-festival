export type FamilyMember = { name: string; role: string; letter: string; isGuardian: boolean };

export type FamilyMembersModel = {
  familyName: string;
  familyTagline: string;
  familyDescription: string;
  memberSummary: string;
  members: FamilyMember[];
  pendingChildRequestName?: string;
};

export type FamilyMembersProps = {
  model: FamilyMembersModel;
  onBack?: () => void;
  onEdit?: () => void;
  onSelectMember?: (member: FamilyMember) => void;
  onInvite?: () => void;
  onViewRequests?: () => void;
};
