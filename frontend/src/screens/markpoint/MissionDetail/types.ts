export type MissionDetailModel = {
  title: string;
  description: string;
  reward: string;
  progressPercent: number;
  completedCount: number;
  totalCount: number;
  checklist: { label: string; done: boolean }[];
  photoNotice: string;
  submitNotice: string;
};

export type MissionDetailProps = {
  model: MissionDetailModel;
  onBack?: () => void;
  onMenu?: () => void;
  onSubmit?: () => void;
  /** Toggles one checklist item by its index in `model.checklist`. Omitted
   *  (no-op) when the mission has no checklist to toggle. */
  onToggleItem?: (index: number) => void;
};
