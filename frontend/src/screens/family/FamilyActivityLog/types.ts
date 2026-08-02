export type ActivityLogEvent = { initial: string; tone: 'purple' | 'blue' | 'green' | 'yellow' | 'red'; title: string; detail?: string; time: string };
export type ActivityLogDay = { label: string; events: ActivityLogEvent[] };
export type FamilyActivityLogModel = { title: string; filters: string[]; activeFilter: string; days: ActivityLogDay[] };
export type FamilyActivityLogProps = { model: FamilyActivityLogModel; onBack?: () => void; onFilter?: (name: string) => void };
