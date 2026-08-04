export type MissionStatisticsDashboardModel={title:string;completion:string;active:string;points:string;members:{name:string;value:number}[]};
export type MissionStatisticsDashboardProps={
  model:MissionStatisticsDashboardModel;
  /** Product embeds this Screen inside its own modal/overlay (AdminLayout
   *  already owns the real Sidebar). Detached Preview omits this prop. */
  embedded?:boolean;
  onOpenFilter?:()=>void;
  onClose?:()=>void;
};
