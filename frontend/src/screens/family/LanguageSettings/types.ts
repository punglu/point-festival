export type LanguageOption = { label: string; selected: boolean };
export type LanguageSettingsModel = { title: string; options: LanguageOption[]; notice: string };
export type LanguageSettingsProps = { model: LanguageSettingsModel; onBack?: () => void; onSelect?: (label: string) => void };
