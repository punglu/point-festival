export type SettingsNavItem = { key: string; label: string; icon: string; detail?: string };
export type SettingsToggleItem = { key: string; label: string; icon: string; on: boolean };

export type SettingsListModel = {
  playerInitial: string;
  playerName: string;
  playerMeta: string;
  navGroups: { title: string; items: SettingsNavItem[] }[];
  toggleGroups: { title: string; items: SettingsToggleItem[] }[];
  version: string;
};

export type SettingsListProps = {
  model: SettingsListModel;
  onBack?: () => void;
  onOpenProfile?: () => void;
  onSelectNav?: (item: SettingsNavItem) => void;
  onToggle?: (item: SettingsToggleItem) => void;
  onLogout?: () => void;
};
