export type ThemeMode = { label: string; selected: boolean };
export type ThemeSettingsModel = {
  title: string;
  modes: ThemeMode[];
  largeText: boolean;
  highContrast: boolean;
  fontScale: number;
  previewText: string;
};
export type ThemeSettingsProps = {
  model: ThemeSettingsModel;
  onBack?: () => void;
  onSelectMode?: (label: string) => void;
  onToggle?: (key: 'largeText' | 'highContrast') => void;
};
