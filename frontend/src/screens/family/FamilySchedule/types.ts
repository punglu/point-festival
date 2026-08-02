export type ScheduleEvent = { id: string; color: string; title: string; meta: string; people: string[] };
export type CalendarDay = { day: string; marker: string };

export type FamilyScheduleModel = {
  weekSummary: string;
  monthLabel: string;
  weekdays: string[];
  days: CalendarDay[];
  todayLabel: string;
  todayEvents: ScheduleEvent[];
  upcomingEvents: ScheduleEvent[];
};

export type FamilyScheduleProps = {
  model: FamilyScheduleModel;
  onBack?: () => void;
  onAddSchedule?: () => void;
  onSelectEvent?: (event: ScheduleEvent) => void;
};
