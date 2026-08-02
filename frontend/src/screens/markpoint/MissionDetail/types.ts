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
};
