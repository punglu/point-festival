export type ScheduleAttendee = { name: string; tone: 'blue' | 'red' | 'purple' | 'green' };
export type ScheduleDetailModel = {
  category: string;
  title: string;
  dateTime: string;
  place: string;
  repeat: string;
  attendees: ScheduleAttendee[];
};
export type ScheduleDetailProps = { model: ScheduleDetailModel; onBack?: () => void; onEdit?: () => void; onDelete?: () => void };
