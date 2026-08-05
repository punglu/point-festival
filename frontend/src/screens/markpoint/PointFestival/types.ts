export type PointFestivalDay = {
  weekday: string;
  day: string;
  date: string;
};

export type PointFestivalMissionStatusKind = 'complete' | 'progress' | 'pending';

export type PointFestivalMission = {
  id: number;
  title: string;
  subtitle: string;
  reward: string;
  status: string;
  statusKind: PointFestivalMissionStatusKind;
  action?: string;
  progress?: string;
  count?: string;
};

export type PointFestivalCheerMessage = {
  name: string;
  tone: string;
  message: string;
  time: string;
};

export type PointFestivalHistoryEntry = {
  title: string;
  subtitle: string;
  amount: string;
  time: string;
};

export type PointFestivalScreenModel = {
  playerName: string;
  level: number;
  levelProgressPercent: number;
  earnedLabel: string;
  levelHint: string;
  todayEarned: number;
  remainingMissions: number;
  currentBalance: number;
  /** Week-picker + missions-for-selected-day + point-history zone. Optional:
   * the real Product currently keeps its own already-real, already-tested
   * weekly day-list (a committed E2E spec — `03-target-ui.spec.ts` — asserts
   * its exact DOM shape: an `<ol>`/`<li>` list with every day of the cycle
   * always expanded, a `data-today` marker, and a direct submit button per
   * mission — a structurally different contract than this Screen's own
   * single-selected-day picker). Only the detached Preview renders this zone,
   * via its own fixture. See this task's own handoff for the full reasoning. */
  weekLabel?: string;
  days?: PointFestivalDay[];
  selectedDate?: string;
  /** No backend "family cheer message" capability exists today — omitted (undefined)
   * for the real Product, supplied only by the detached Preview's own fixture. */
  cheerMessages?: PointFestivalCheerMessage[];
  missionsTitle?: string;
  missions?: PointFestivalMission[];
  /** Most recent real deduction, if any. Omitted (undefined) when there is none. */
  historyEntry?: PointFestivalHistoryEntry;
};

export type PointFestivalScreenProps = {
  model: PointFestivalScreenModel;
  /** Default true. The real Product passes false — see `PointFestivalScreenModel`'s
   * own doc comment on `weekLabel` for why. */
  showWeeklySection?: boolean;
  onLogout?: () => void;
  onSelectDay?: (date: string) => void;
  onSelectMission?: (missionId: number) => void;
  onHistoryClick?: () => void;
};
