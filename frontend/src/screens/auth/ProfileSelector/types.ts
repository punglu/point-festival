export type ProfileSelectorProfile = {
  name: string;
  level?: string;
  points?: string;
  locked?: boolean;
  lockReason?: string;
  lockRetry?: string;
};

export type ProfileSelectorScreenModel = {
  brand: string;
  tagline: string;
  heading: string;
  profiles: ProfileSelectorProfile[];
  lockedNotice?: { title: string; body: string };
  adminLoginLabel: string;
};

export type ProfileSelectorScreenProps = {
  model: ProfileSelectorScreenModel;
  onSelect?: (name: string) => void;
  onAdminLogin?: () => void;
};
