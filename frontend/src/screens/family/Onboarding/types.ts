export type OnboardingModel = {
  familyName: string;
};

export type OnboardingProps = {
  model: OnboardingModel;
  onFamilyNameChange?: (value: string) => void;
  onNext?: () => void;
  onHaveInviteCode?: () => void;
};
