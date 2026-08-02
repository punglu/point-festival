export type ProfileSelectorScreenModel = {
  title: string;
  subtitle: string;
  profiles: Array<{ name: string; role: string; initial: string }>;
};

export type ProfileSelectorScreenProps = {
  model: ProfileSelectorScreenModel;
  onSelect?: (name: string) => void;
};
