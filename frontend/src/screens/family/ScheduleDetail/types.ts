export type ScheduleDetailModel={title:string;date:string;time:string;place:string;description:string;attendees:string[]};
export type ScheduleDetailProps={model:ScheduleDetailModel;onBack?:()=>void;onEdit?:()=>void};
