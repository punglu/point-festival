import type { ReactNode } from 'react';

export type ParentDashboardStatCardKey = 'points' | 'active' | 'pending' | 'completed';

export type ParentDashboardStatCard = {
  key: ParentDashboardStatCardKey;
  label: string;
  value: string | number;
  subtext?: string;
  subtextColor?: string;
};

export type ParentDashboardModel = {
  title: string;
  cycleLabel?: string;
  statCards: ParentDashboardStatCard[];
  selectedStatCard: ParentDashboardStatCardKey | null;
};

export type ParentDashboardProps = {
  model: ParentDashboardModel;
  /** Product embeds this Screen inside AdminLayout's own real Sidebar --
   *  suppresses the frozen preview's own decorative sidebar. Detached
   *  Preview omits this prop. */
  embedded?: boolean;
  onRefresh?: () => void;
  onOpenMissions?: () => void;
  onSelectStatCard?: (key: ParentDashboardStatCardKey) => void;
  /** Real per-card drill-in (CardDetailTable + its own trigger buttons),
   *  shown only while a stat card is selected. */
  detailPanelSlot?: ReactNode;
  /**
   * The real product's own 6 dashboard sections, composed as named slots.
   * Each is an already-real, independently stateful component
   * (PlayerStatusCard / BalanceSection / RecentAlerts / PendingMissionCard /
   * WeeklyActivityChart / MissionRanking) -- reimplementing their internal
   * data/interaction logic as generic typed props would duplicate real
   * business logic a Canonical Screen must never own (it never fetches).
   * `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)`'s own
   * "real page richer than frozen mockup" finding for 1b/1c/1d is the
   * same shape this slot composition resolves for 2i.
   */
  playerStatusSlot?: ReactNode;
  balanceSlot?: ReactNode;
  alertsSlot?: ReactNode;
  pendingMissionSlot?: ReactNode;
  weeklyActivitySlot?: ReactNode;
  rankingSlot?: ReactNode;
  /** Overlay/modal layer (canonical 1m/2m/2x/3b + any Product-only
   *  modals), rendered last, unaffected by this Screen's own layout. */
  overlaysSlot?: ReactNode;
};
