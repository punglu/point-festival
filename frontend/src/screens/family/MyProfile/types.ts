export type MyProfileListItem = { key: string; name: string; value: string; icon: string };

export type MyProfileModel = {
  avatarInitial: string;
  playerName: string;
  levelLabel: string;
  familyMeta: string;
  stats: { name: string; value: string }[];
  levelProgressLabel: string;
  levelProgressPercent: number;
  levelHint: string;
  activity: MyProfileListItem[];
  settings: MyProfileListItem[];
};

export type MyProfileProps = {
  model: MyProfileModel;
  onEditProfile?: () => void;
  onSelectItem?: (item: MyProfileListItem) => void;
  onOpenAllSettings?: () => void;
  onLogout?: () => void;
};
