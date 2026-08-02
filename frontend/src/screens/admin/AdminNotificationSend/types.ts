export type AdminNotificationSendModel={title:string;recipients:string;subject:string;message:string};
export type AdminNotificationSendProps={model:AdminNotificationSendModel;onSend?:()=>void;onCancel?:()=>void};
