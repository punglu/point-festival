export type PointPolicyEditorModel={title:string;monthlyLimit:string;dailyLimit:string;approvalRequired:boolean;notice:string};
export type PointPolicyEditorProps={model:PointPolicyEditorModel;onSave?:()=>void;onClose?:()=>void};
