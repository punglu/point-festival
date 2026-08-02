export type MissionStatisticsDashboardModel={title:string;completion:string;active:string;points:string;members:{name:string;value:number}[]};
export type MissionStatisticsDashboardProps={model:MissionStatisticsDashboardModel;onOpenFilter?:()=>void};
