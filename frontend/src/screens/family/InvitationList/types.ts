export type Invitation={name:string;email:string;sentAt:string;status:string};
export type InvitationListModel={title:string;invitations:Invitation[]};
export type InvitationListProps={model:InvitationListModel;onBack?:()=>void;onResend?:(email:string)=>void;onCancel?:(email:string)=>void};
