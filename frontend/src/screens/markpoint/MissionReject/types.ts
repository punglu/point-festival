export type MissionRejectModel = {
  missionIcon: string;
  missionTitle: string;
  missionSummary: string;
  reviewerName: string;
  reason: string;
};

export type MissionRejectProps = {
  model: MissionRejectModel;
  onBack?: () => void;
  onRetry?: () => void;
};
