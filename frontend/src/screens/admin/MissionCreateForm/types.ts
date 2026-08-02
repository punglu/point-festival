export type MissionCreateFormModel = {
  title: string;
  description: string;
  assignees: string;
  points: number;
};

export type MissionCreateFormProps = {
  model: MissionCreateFormModel;
  onCancel?: () => void;
  onCreate?: () => void;
};
