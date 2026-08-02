export type ChatSettingsItem = { name: string; description: string; hasToggle?: boolean };
export type ChatSettingsMember = { name: string };

export type ChatSettingsModel = {
  roomName: string;
  memberSummary: string;
  items: ChatSettingsItem[];
  members: ChatSettingsMember[];
};

export type ChatSettingsProps = {
  model: ChatSettingsModel;
  onBack?: () => void;
  onOpenItem?: (item: ChatSettingsItem) => void;
  onLeave?: () => void;
};
