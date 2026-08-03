/**
 * Family Activity Log API client (W7.5 Phase D, SLICE-FAMILY-ACTIVITY-LOG,
 * canonical `2r`). Reads existing Markpoint audit events -- no new
 * event-logging table exists.
 */
import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

type Schemas = components['schemas'];

export type ActivityLogEntry = Schemas['ActivityLogEntryOut'];

export async function listActivityLog(familyId: number, signal?: AbortSignal): Promise<ActivityLogEntry[]> {
  const { data } = await httpClient.get<ActivityLogEntry[]>(`/api/families/${familyId}/activity-log`, { signal });
  return data;
}
