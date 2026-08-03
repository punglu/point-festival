/**
 * Family Schedule API client (W7.5 Phase D, SLICE-SCHEDULE, canonical
 * `1g`/`1o`/`2u`). `3a` (캘린더 공유)'s external Google/Apple Calendar sync
 * and webcal subscription link are **not** part of this Slice -- that is a
 * real external-service OAuth/feed-generation integration this repository
 * has no credentials or infra for, out of scope same as file storage.
 */
import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

type Schemas = components['schemas'];

export type FamilyScheduleEvent = Schemas['ScheduleEventOut'];

export async function listScheduleEvents(familyId: number, signal?: AbortSignal): Promise<FamilyScheduleEvent[]> {
  const { data } = await httpClient.get<FamilyScheduleEvent[]>(`/api/families/${familyId}/schedule-events`, { signal });
  return data;
}

export async function createScheduleEvent(
  familyId: number,
  body: { title: string; starts_at: string; location?: string | null; memo?: string | null; attendee_membership_ids?: number[] | null },
): Promise<FamilyScheduleEvent> {
  const { data } = await httpClient.post<FamilyScheduleEvent>(`/api/families/${familyId}/schedule-events`, body);
  return data;
}

export async function updateScheduleEvent(
  familyId: number,
  eventId: number,
  body: Partial<{ title: string; starts_at: string; location: string | null; memo: string | null; attendee_membership_ids: number[] | null }>,
): Promise<FamilyScheduleEvent> {
  const { data } = await httpClient.patch<FamilyScheduleEvent>(`/api/families/${familyId}/schedule-events/${eventId}`, body);
  return data;
}

export async function deleteScheduleEvent(familyId: number, eventId: number): Promise<void> {
  await httpClient.delete(`/api/families/${familyId}/schedule-events/${eventId}`);
}
