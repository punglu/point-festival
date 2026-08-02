export type NotificationPreference={label:string;enabled:boolean;detail?:string};
export type NotificationPreferencesModel={title:string;groups:{title:string;items:NotificationPreference[]}[]};
export type NotificationPreferencesProps={model:NotificationPreferencesModel;onBack?:()=>void;onToggle?: (label:string)=>void};
