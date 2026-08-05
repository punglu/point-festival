import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyMembersScreen, familyMembersFixture } from '../../screens/family/FamilyMembers';
import type { FamilyMember } from '../../screens/family/FamilyMembers';
import { InvitationListScreen, invitationListFixture } from '../../screens/family/InvitationList';
import { FamilyActivityLogScreen, familyActivityLogFixture } from '../../screens/family/FamilyActivityLog';
import { FamilyInviteCancelScreen, familyInviteCancelFixture } from '../../screens/family/FamilyInviteCancel';
import { ChildInviteScreen, childInviteFixture } from '../../screens/family/ChildInvite';
import { listFamilyMembers, type FamilyMembershipSummary } from '../../shared/api/familyApi';
import { listActivityLog, type ActivityLogEntry } from '../../shared/api/familyActivityLogApi';
import { toActivityEvent } from '../../shared/family/activityLogFormat';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './FamilyMembersPage.module.css';
import type { ActivityLogDay, ActivityLogEvent } from '../../screens/family/FamilyActivityLog';

type View = 'main' | 'invitations' | 'cancel-invite' | 'activity' | 'child-invite';

function dayLabel(iso: string): string {
  const date = new Date(iso);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === today.toDateString()) return '오늘';
  if (date.toDateString() === yesterday.toDateString()) return '어제';
  return date.toLocaleDateString('ko-KR');
}

function toActivityDays(entries: ActivityLogEntry[]): ActivityLogDay[] {
  const byDay = new Map<string, ActivityLogEvent[]>();
  for (const entry of entries) {
    const label = dayLabel(entry.occurred_at);
    const list = byDay.get(label) ?? [];
    list.push(toActivityEvent(entry));
    byDay.set(label, list);
  }
  return Array.from(byDay.entries()).map(([label, events]) => ({ label, events }));
}

function toFamilyMember(membership: FamilyMembershipSummary): FamilyMember {
  const isGuardian = membership.roles.some((r) => r.scope_type === 'FAMILY' && (r.code === 'owner' || r.code === 'admin'));
  const roleLabel = membership.roles.find((r) => r.scope_type === 'FAMILY')?.code === 'owner' ? '가족 관리자'
    : isGuardian ? '보호자' : '구성원';
  return {
    name: membership.account_display_name,
    role: roleLabel,
    letter: membership.account_display_name.slice(0, 2),
    isGuardian,
  };
}

/**
 * `/family/members` — canonical 1q (가족 구성원, CHILD_OF 1b) with 2f/2p/2r/3i
 * as nested views/overlays per the W7.4 Ownership Matrix. W7.5: `1q`'s member
 * list now calls the real `GET /api/families/{family_id}/members` (W7.5
 * Matrix, EXTEND_EXISTING_API — required an additive `account_display_name`
 * field on `MembershipSummary`, since the response otherwise only carried
 * `account_id`). Family name/tagline/description remain fixture-sourced
 * (static presentational copy, not user data). 2f/2p/2r/3i remain fixture —
 * see the Matrix for their own status.
 */
export function FamilyMembersPage() {
  const navigate = useNavigate();
  const activeFamilyId = useFamilyContextStore((state) => state.activeFamilyId);
  const [view, setView] = useState<View>('main');
  const [activeFilter, setActiveFilter] = useState(familyActivityLogFixture.activeFilter);
  const [cancelInvite, setCancelInvite] = useState<string | null>(null);
  const [members, setMembers] = useState<FamilyMember[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [activityLog, setActivityLog] = useState<ActivityLogEntry[] | null>(null);
  const [activityError, setActivityError] = useState<string | null>(null);

  useEffect(() => {
    if (activeFamilyId === null) return;
    const controller = new AbortController();
    setLoadError(null);
    listFamilyMembers(activeFamilyId, controller.signal)
      .then((data) => setMembers(data.map(toFamilyMember)))
      .catch(() => { if (!controller.signal.aborted) setLoadError('가족 구성원을 불러오지 못했어요.'); });
    return () => controller.abort();
  }, [activeFamilyId]);

  useEffect(() => {
    if (activeFamilyId === null || view !== 'activity') return undefined;
    const controller = new AbortController();
    setActivityError(null);
    listActivityLog(activeFamilyId, controller.signal)
      .then(setActivityLog)
      .catch(() => { if (!controller.signal.aborted) setActivityError('활동 로그를 불러오지 못했어요.'); });
    return () => controller.abort();
  }, [activeFamilyId, view]);

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
    // 2r — reads the existing MarkpointAuditEvent table (no new log table,
    // W7.5 Phase D SLICE-FAMILY-ACTIVITY-LOG). Filter dropdown stays the
    // fixture's own filter labels (전체/이름별/부모): filtering by a
    // specific member's name is real (matches actor_display_name), but
    // '부모' has no real role-based concept to filter by here and is left
    // as a no-op rather than fabricating a guardian/child split.
    const days = activityLog === null ? [] : toActivityDays(activityLog);
    const filteredDays = activeFilter === '전체' || activeFilter === '부모'
      ? days
      : days.map((d) => ({ ...d, events: d.events.filter((e) => e.title.startsWith(activeFilter)) })).filter((d) => d.events.length > 0);
    return (
      <div className={styles.wrap}>
        <FamilyActivityLogScreen
          model={{
            ...familyActivityLogFixture,
            activeFilter,
            days: activityLog === null ? [] : filteredDays,
          }}
          onBack={() => setView('main')}
          onFilter={setActiveFilter}
        />
        {activityError && <p className={styles.error} role="alert">{activityError}</p>}
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

  // Load failure must never fall back to the fixture's fake member list --
  // a real empty list plus the real error message only.
  const resolvedMembers = members ?? [];
  return (
    <div className={styles.wrap}>
      <FamilyMembersScreen
        model={{
          ...familyMembersFixture,
          members: resolvedMembers,
          memberSummary: loadError ?? `우리 가족 ${resolvedMembers.length}명`,
        }}
        onBack={() => navigate('/family')}
        onEdit={() => undefined}
        onSelectMember={() => { setActiveFilter(familyActivityLogFixture.activeFilter); setView('activity'); }}
        onInvite={() => setView('invitations')}
        onViewRequests={() => setView('child-invite')}
      />
    </div>
  );
}
