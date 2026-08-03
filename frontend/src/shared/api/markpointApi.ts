/**
 * Markpoint Target API client.
 *
 * Every wire type here comes from `generated/openapi.d.ts`, regenerated from
 * the live backend schema. Nothing is hand-declared: the one class of defect
 * this project has already shipped twice is a frontend literal drifting from a
 * backend value while both sides remain typed `string`, and re-typing responses
 * by hand is how that happens.
 *
 * Two boundaries this file holds:
 *
 * - **Family scope comes from the caller, never from a store.** Every
 *   family-scoped call takes `familyId` as an argument. Reading an "active
 *   family" out of a store inside the client would make a UI convenience into
 *   an authorization input, which D1 forbids — and the server would still
 *   refuse, so the bug would surface as a confusing 403 rather than a clear
 *   programming error.
 * - **No response is reshaped.** The UI renders what the server said. A
 *   client-side derived total or status would be a second source of truth able
 *   to disagree with the Ledger.
 */
import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

type Schemas = components['schemas'];

export type MarkpointMission = Schemas['MissionOut'];
export type MarkpointLedgerEntry = Schemas['LedgerOut'];
export type MarkpointBalance = Schemas['BalanceOut'];
export type MarkpointLevel = Schemas['LevelOut'];
export type MarkpointTemplate = Schemas['TemplateOut'];
export type MarkpointCycleConfig = Schemas['CycleConfigOut'];

/**
 * The server's mission status enum. Kept as a union of literals rather than a
 * loose `string` so a screen cannot invent a state the backend never emits —
 * the frontend must never infer or advance a mission's status on its own.
 */
export type MissionStatus =
  | 'active'
  | 'pending_approval'
  | 'completed'
  | 'rejected'
  | 'cancelled'
  | 'expired';

export const MISSION_STATUS_LABEL: Record<MissionStatus, string> = {
  active: '진행 중',
  pending_approval: '승인 대기',
  completed: '완료',
  rejected: '반려됨',
  cancelled: '취소됨',
  expired: '기간 만료',
};

/** Untyped in the generated schema (the route returns a plain dict), so the
 *  shape is declared here to match `service.own_projection` field for field. */
export interface MarkpointProjection {
  family_group_id: number;
  family_membership_id: number;
  cycle_type: string;
  period_start: string;
  period_end: string;
  today: string;
  today_earned: number;
  today_deducted: number;
  weekly_earned: number;
  weekly_deducted: number;
  current_balance: number;
  lifetime_earned: number;
  lifetime_spent: number;
  remaining_missions: number;
  expected_points: number;
}

export interface MarkpointWeeklyDay {
  date: string;
  missions: {
    id: number;
    title: string;
    status: MissionStatus;
    reward_amount: number;
    template_id: number | null;
    description: string | null;
    checklist: { label: string; done: boolean }[] | null;
    rejection_reason: string | null;
    reviewer_display_name: string | null;
  }[];
  remaining: number;
  completed: number;
}

export interface MarkpointWeekly {
  family_group_id: number;
  family_membership_id: number;
  cycle_type: string;
  period_start: string;
  period_end: string;
  days: MarkpointWeeklyDay[];
  total_missions: number;
  remaining_missions: number;
  completed_missions: number;
  expected_points: number;
  earned_points: number;
}

export interface MarkpointDeduction {
  id: number;
  amount: number;
  entry_type: string;
  reason: string | null;
  reversal_of_entry_id: number | null;
  /** True when a later reversal points at this entry. The original row is
   *  never edited, so this is how the UI shows "this was corrected" without
   *  implying the amount changed in place. */
  corrected: boolean;
  occurred_at: string;
  created_by_membership_id: number | null;
}

// ---------------------------------------------------------------------------
// Personal (`/me`) — the caller's own data in one family
// ---------------------------------------------------------------------------

export async function getProjection(familyId: number, signal?: AbortSignal) {
  const { data } = await httpClient.get<MarkpointProjection>('/api/me/markpoint/projection', {
    params: { family_id: familyId },
    signal,
  });
  return data;
}

export async function getWeekly(familyId: number, signal?: AbortSignal) {
  const { data } = await httpClient.get<MarkpointWeekly>('/api/me/markpoint/weekly', {
    params: { family_id: familyId },
    signal,
  });
  return data;
}

export async function getLevel(familyId: number, signal?: AbortSignal) {
  const { data } = await httpClient.get<MarkpointLevel>('/api/me/markpoint/level', {
    params: { family_id: familyId },
    signal,
  });
  return data;
}

export async function getOwnMissions(familyId: number, signal?: AbortSignal) {
  const { data } = await httpClient.get<MarkpointMission[]>('/api/me/markpoint/missions', {
    params: { family_id: familyId },
    signal,
  });
  return data;
}

export async function getDeductionHistory(familyId: number, signal?: AbortSignal) {
  const { data } = await httpClient.get<MarkpointDeduction[]>(
    '/api/me/markpoint/deductions/history',
    { params: { family_id: familyId }, signal },
  );
  return data;
}

// ---------------------------------------------------------------------------
// Mission lifecycle
// ---------------------------------------------------------------------------

export async function submitMission(familyId: number, missionId: number) {
  const { data } = await httpClient.post<MarkpointMission>(
    `/api/families/${familyId}/markpoint/missions/${missionId}/submit`,
  );
  return data;
}

export async function approveMission(familyId: number, missionId: number) {
  const { data } = await httpClient.post<MarkpointMission>(
    `/api/families/${familyId}/markpoint/missions/${missionId}/approve`,
  );
  return data;
}

export async function rejectMission(familyId: number, missionId: number, reason: string) {
  const { data } = await httpClient.post<MarkpointMission>(
    `/api/families/${familyId}/markpoint/missions/${missionId}/reject`,
    { reason },
  );
  return data;
}

export async function cancelMission(familyId: number, missionId: number, reason: string) {
  const { data } = await httpClient.post<MarkpointMission>(
    `/api/families/${familyId}/markpoint/missions/${missionId}/cancel`,
    { reason },
  );
  return data;
}

export async function createMission(
  familyId: number,
  body: {
    assignee_membership_id: number;
    title: string;
    scheduled_for: string;
    reward_amount: number;
    description?: string | null;
    checklist?: string[] | null;
  },
) {
  const { data } = await httpClient.post<MarkpointMission>(
    `/api/families/${familyId}/markpoint/missions`,
    body,
  );
  return data;
}

/** Assignee toggles their own checklist before submitting (1k). */
export async function updateMissionChecklist(
  familyId: number,
  missionId: number,
  items: { label: string; done: boolean }[],
) {
  const { data } = await httpClient.patch<MarkpointMission>(
    `/api/families/${familyId}/markpoint/missions/${missionId}/checklist`,
    { items },
  );
  return data;
}

// ---------------------------------------------------------------------------
// Admin — mission list, filters, bulk approval
// ---------------------------------------------------------------------------

export interface AdminMissionFilters {
  assignee_membership_id?: number;
  mission_status?: MissionStatus;
  template_id?: number;
  date_from?: string;
  date_to?: string;
  limit?: number;
}

export async function listMissions(
  familyId: number,
  filters: AdminMissionFilters = {},
  signal?: AbortSignal,
) {
  const { data } = await httpClient.get<MarkpointMission[]>(
    `/api/families/${familyId}/markpoint/missions`,
    { params: filters, signal },
  );
  return data;
}

export interface BulkApprovalResult {
  requested: number;
  approved: number[];
  skipped_already_completed: number[];
}

/**
 * All-or-nothing by product contract. A rejected batch changes nothing, so the
 * caller must not render a partial result — see `MarkpointAdmin`'s handling.
 */
export async function bulkApproveMissions(familyId: number, missionIds: number[]) {
  const { data } = await httpClient.post<BulkApprovalResult>(
    `/api/families/${familyId}/markpoint/missions/bulk-approve`,
    { mission_ids: missionIds },
  );
  return data;
}

// ---------------------------------------------------------------------------
// Admin — templates, materialization, cycle config
// ---------------------------------------------------------------------------

export async function listTemplates(familyId: number, signal?: AbortSignal) {
  const { data } = await httpClient.get<MarkpointTemplate[]>(
    `/api/families/${familyId}/markpoint/templates`,
    { signal },
  );
  return data;
}

export async function createTemplate(
  familyId: number,
  body: {
    assignee_membership_id: number;
    title: string;
    reward_amount: number;
    cycle_type: string;
    start_date: string;
    end_date?: string | null;
    day_of_week?: number | null;
  },
) {
  const { data } = await httpClient.post<MarkpointTemplate>(
    `/api/families/${familyId}/markpoint/templates`,
    body,
  );
  return data;
}

export async function deactivateTemplate(familyId: number, templateId: number) {
  const { data } = await httpClient.delete<MarkpointTemplate>(
    `/api/families/${familyId}/markpoint/templates/${templateId}`,
  );
  return data;
}

export interface MaterializationResult {
  window_start: string;
  window_end: string;
  templates_processed: number;
  missions_created: number;
  missions_skipped_existing: number;
}

export async function materializeWindow(familyId: number, templateId?: number) {
  const { data } = await httpClient.post<MaterializationResult>(
    `/api/families/${familyId}/markpoint/templates/materialize-window`,
    undefined,
    { params: templateId ? { template_id: templateId } : undefined },
  );
  return data;
}

export async function getCycleConfig(familyId: number, signal?: AbortSignal) {
  const { data } = await httpClient.get<MarkpointCycleConfig>(
    `/api/families/${familyId}/markpoint/config`,
    { signal },
  );
  return data;
}

export async function updateCycleConfig(
  familyId: number,
  body: { cycle_type?: string | null; display_name?: string | null },
) {
  const { data } = await httpClient.put<MarkpointCycleConfig>(
    `/api/families/${familyId}/markpoint/config`,
    body,
  );
  return data;
}

// ---------------------------------------------------------------------------
// Admin — point adjustment and deduction correction
// ---------------------------------------------------------------------------

export async function adjustPoints(
  familyId: number,
  body: { beneficiary_membership_id: number; amount: number; reason: string; idempotency_key: string },
) {
  const { data } = await httpClient.post<MarkpointLedgerEntry>(
    `/api/families/${familyId}/markpoint/ledger/adjustments`,
    body,
  );
  return data;
}

export interface DeductionCorrectionResult {
  original_entry_id: number;
  original_amount: number;
  reversal_entry_id: number;
  replacement_entry_id: number | null;
  new_amount: number | null;
}

/**
 * Appends a reversal and, when `newAmount` is given, a replacement. The
 * original row is never modified — the UI must reflect that rather than
 * showing the old entry as edited.
 */
export async function correctDeduction(
  familyId: number,
  entryId: number,
  body: { new_amount: number | null; reason: string },
) {
  const { data } = await httpClient.post<DeductionCorrectionResult>(
    `/api/families/${familyId}/markpoint/ledger/${entryId}/correct`,
    body,
  );
  return data;
}
