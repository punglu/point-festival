export type ProfileSelectorProfile = {
  name: string;
  /** Real product identity key (e.g. player id). Falls back to `name` when absent, so the
   * fixture-driven Preview (which has no id) keeps its prior behavior unchanged. */
  id?: string;
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
  /** Receives `profile.id` when present, else `profile.name` — see `ProfileSelectorProfile.id`. */
  onSelect?: (key: string) => void;
  onAdminLogin?: () => void;
};
