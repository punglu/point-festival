export type MissionApprovalItem = {
  id: number;
  playerName: string;
  title: string;
  meta: string;
};

export type MissionApprovalModel = {
  pendingCount: number;
  approvedTodayCount: number;
  rejectedTodayCount: number;
  pendingPoints: number;
  items: MissionApprovalItem[];
};

export type MissionApprovalProps = {
  model: MissionApprovalModel;
  /** Product embeds this Screen inside its own modal/overlay (AdminLayout
   *  already owns the real Sidebar) -- suppresses the frozen preview's own
   *  decorative sidebar. Detached Preview omits this prop. */
  embedded?: boolean;
  onApprove?: (id: number) => void;
  onReject?: (id: number) => void;
  onClose?: () => void;
};
