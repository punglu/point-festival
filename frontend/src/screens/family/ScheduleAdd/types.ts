export type ScheduleAddModel = {
  title: string;
  date: string;
  time: string;
  place: string;
  attendees: { name: string; selected: boolean }[];
  reminder: string;
  memo: string;
};

export type ScheduleAddProps = {
  model: ScheduleAddModel;
  onBack?: () => void;
  onSave?: () => void;
  onChangeField?: (field: keyof ScheduleAddModel, value: string) => void;
  onToggleAttendee?: (name: string) => void;
};
