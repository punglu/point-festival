import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyMembersScreen, familyMembersFixture } from '../../screens/family/FamilyMembers';
import { InvitationListScreen, invitationListFixture } from '../../screens/family/InvitationList';
import { FamilyActivityLogScreen, familyActivityLogFixture } from '../../screens/family/FamilyActivityLog';
import { FamilyInviteCancelScreen, familyInviteCancelFixture } from '../../screens/family/FamilyInviteCancel';
import { ChildInviteScreen, childInviteFixture } from '../../screens/family/ChildInvite';
import styles from './FamilyMembersPage.module.css';

type View = 'main' | 'invitations' | 'cancel-invite' | 'activity' | 'child-invite';

/**
 * `/family/members` — canonical 1q (가족 구성원, CHILD_OF 1b) with 2f/2p/2r/3i
 * as nested views/overlays per the W7.4 Ownership Matrix.
 */
export function FamilyMembersPage() {
  const navigate = useNavigate();
  const [view, setView] = useState<View>('main');
  const [activeFilter, setActiveFilter] = useState(familyActivityLogFixture.activeFilter);
  const [cancelInvite, setCancelInvite] = useState<string | null>(null);

  if (view === 'invitations') {
    return (
      <div className={styles.wrap}>
        <InvitationListScreen
          model={invitationListFixture}
          onBack={() => setView('main')}
          onResend={() => undefined}
          onCancel={(email) => { setCancelInvite(email); setView('cancel-invite'); }}
        />
      </div>
    );
  }

  if (view === 'cancel-invite') {
    return (
      <div className={styles.wrap}>
        <FamilyInviteCancelScreen
          model={{ ...familyInviteCancelFixture, invitee: cancelInvite ?? familyInviteCancelFixture.invitee }}
          onBack={() => setView('invitations')}
          onConfirm={() => setView('invitations')}
        />
      </div>
    );
  }

  if (view === 'activity') {
    return (
      <div className={styles.wrap}>
        <FamilyActivityLogScreen
          model={{ ...familyActivityLogFixture, activeFilter }}
          onBack={() => setView('main')}
          onFilter={setActiveFilter}
        />
      </div>
    );
  }

  if (view === 'child-invite') {
    return (
      <div className={styles.wrap}>
        <ChildInviteScreen
          model={childInviteFixture}
          onApprove={() => setView('main')}
          onDismiss={() => setView('main')}
        />
      </div>
    );
  }

  return (
    <div className={styles.wrap}>
      <FamilyMembersScreen
        model={familyMembersFixture}
        onBack={() => navigate('/family')}
        onEdit={() => undefined}
        onSelectMember={() => { setActiveFilter(familyActivityLogFixture.activeFilter); setView('activity'); }}
        onInvite={() => setView('invitations')}
        onViewRequests={() => setView('child-invite')}
      />
    </div>
  );
}
