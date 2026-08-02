export type FamilyInviteAcceptanceModel={familyName:string;inviter:string;message:string};
export type FamilyInviteAcceptanceProps={model:FamilyInviteAcceptanceModel;onAccept?:()=>void;onDecline?:()=>void};
