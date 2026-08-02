import { InvitationListScreen, invitationListFixture } from '../../screens/family/InvitationList';
export function InvitationListPreview(){return <InvitationListScreen model={invitationListFixture} onResend={()=>undefined} onCancel={()=>undefined}/>;}
