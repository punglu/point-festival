export type AdminNotificationSendModel={title:string;recipients:string;subject:string;message:string;isSending?:boolean;errorMessage?:string|null};
export type AdminNotificationSendProps={model:AdminNotificationSendModel;onSend?:(payload:{subject:string;message:string})=>void;onCancel?:()=>void};
