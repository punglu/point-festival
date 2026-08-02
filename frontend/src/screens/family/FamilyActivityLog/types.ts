export type ActivityLogItem={title:string;description:string;time:string;kind:string};
export type FamilyActivityLogModel={title:string;items:ActivityLogItem[]};
export type FamilyActivityLogProps={model:FamilyActivityLogModel;onBack?:()=>void};
