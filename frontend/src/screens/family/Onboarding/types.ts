export type OnboardingModel = {
  familyName: string;
  isSubmitting?: boolean;
  errorMessage?: string | null;
};

export type OnboardingProps = {
  model: OnboardingModel;
  onFamilyNameChange?: (value: string) => void;
  onNext?: () => void;
  onHaveInviteCode?: () => void;
};
