export type UserManagementRecentMission = { name: string; status: string };

// Several of the frozen canonical mockup's stat cells (보유 포인트/누적 획득/
// 교환 횟수/레벨/가입일/알림/보호자 승인) have no real field surfaced to the
// Admin frontend today (no `total_earned`/level/join-date/per-player
// notification-preference in the Admin `Player`/`Mission` API response) --
// a TRUE_FUNCTIONAL_GAP, not an engineering shortcut. Those fields keep
// their exact label/position (visual baseline unchanged) but carry an
// explicit "—" placeholder value instead of a fabricated number.
export type UserManagementDetailModel = {
  name: string;
  roleLabel: string;
  levelLabel: string;
  joinedLabel: string;
  lastActiveLabel: string;
  isActive: boolean;
  pointsLabel: string;
  totalEarnedLabel: string;
  completedMissionsLabel: string;
  redeemCountLabel: string;
  pinStatusLabel: string;
  notificationLabel: string;
  guardianApprovalLabel: string;
  recentMissions: UserManagementRecentMission[];
};

export type UserManagementDetailProps = {
  model: UserManagementDetailModel;
  /** Product embeds this Screen inside its own modal/overlay (AdminLayout
   *  already owns the real Sidebar) -- suppresses the frozen preview's own
   *  decorative sidebar. Detached Preview omits this prop. */
  embedded?: boolean;
  onClose?: () => void;
  onToggleLock?: () => void;
};
