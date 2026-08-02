export type MissionDetailFormModel={title:string;description:string;assignees:string;points:number;history:{name:string;time:string;status:'승인'|'반려'}[]};
export type MissionDetailFormProps={model:MissionDetailFormModel;onClose?:()=>void;onSave?:()=>void;onDelete?:()=>void};
