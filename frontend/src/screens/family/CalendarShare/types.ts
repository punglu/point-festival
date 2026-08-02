export type CalendarShareIntegration = { name: string; on: boolean };
export type CalendarShareTarget = { name: string; shared: boolean };
export type CalendarShareModel = {
  title: string;
  subscriptionLink: string;
  copyLabel: string;
  integrations: CalendarShareIntegration[];
  targets: CalendarShareTarget[];
  confirmLabel: string;
};
export type CalendarShareProps = {
  model: CalendarShareModel;
  onClose?: () => void;
  onShare?: () => void;
  onToggleIntegration?: (name: string) => void;
};
