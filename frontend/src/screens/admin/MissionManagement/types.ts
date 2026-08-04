import type { ReactNode } from 'react';

export type MissionManagementStat = { label: string; value: string };

export type MissionManagementFilterStatus = 'all' | 'active' | 'completed';

export type MissionManagementPlayerOption = { id: number; name: string };

export type MissionManagementRow = {
  id: number;
  /** Rendered as-is inside this Screen's AdminDataGrid -- the Product
   *  Container fills this with the real MissionCard/MissionCardEdit swap
   *  it already used, preserving every per-status conditional action
   *  (approve/reject/edit/edit-template/delete/undo) without this Screen
   *  reimplementing that logic. */
  content: ReactNode;
};

export type MissionManagementModel = {
  stats: MissionManagementStat[];
  playerOptions: MissionManagementPlayerOption[];
  selectedPlayerId: number | null;
  selectedDate: string;
  filterStatus: MissionManagementFilterStatus;
  searchQuery: string;
  rows: MissionManagementRow[];
  canBulkApprove: boolean;
  loading: boolean;
};

export type MissionManagementProps = {
  model: MissionManagementModel;
  /** Product embeds this Screen inside AdminLayout's own real Sidebar --
   *  suppresses the frozen preview's own decorative sidebar. Detached
   *  Preview omits this prop. */
  embedded?: boolean;
  /** Real WeeklyGrid, which already fetches and renders itself -- composed
   *  as a slot since a Canonical Screen must never fetch directly. */
  weekGridSlot?: ReactNode;
  /** Real ProposedMissionSection (child-proposed missions, its own card
   *  grid + approve/reject actions) -- composed as-is for the same reason
   *  as weekGridSlot: reimplementing its layout/actions here would
   *  duplicate real, already-styled, already-tested UI. */
  proposedSlot?: ReactNode;
  onSelectPlayer?: (id: number | null) => void;
  onSelectDate?: (date: string) => void;
  onFilterStatus?: (status: MissionManagementFilterStatus) => void;
  onSearch?: (query: string) => void;
  onOpenImport?: () => void;
  onOpenAdd?: () => void;
  onOpenTemplates?: () => void;
  onBulkApprove?: () => void;
};
