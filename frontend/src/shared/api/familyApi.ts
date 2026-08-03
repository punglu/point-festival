import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

/** Generated wire types stay at this API boundary. */
export type FamilyRole = components['schemas']['RoleSummary'];
export type FamilyMembershipSummary = components['schemas']['MembershipSummary'];
export type FamilyContextStatus = components['schemas']['ServiceSubscriptionSummary']['status'];
export type FamilyServiceSummary = components['schemas']['ServiceSubscriptionSummary'];
export type AccountFamilyContext = components['schemas']['AccountContextResponse'];
export type FamilyCreateRequest = components['schemas']['FamilyCreate'];
export type FamilyCreateResponse = components['schemas']['FamilyResponse'];
export type MeResponse = components['schemas']['MeResponse'];
export type MeUpdateRequest = components['schemas']['MeUpdate'];
export type AuthorizedFamilySummary = components['schemas']['AuthorizedFamilySummary'];

export async function getAccountFamilyContext(signal?: AbortSignal): Promise<AccountFamilyContext> {
  const { data } = await httpClient.get<AccountFamilyContext>('/api/account-context', { signal });
  return data;
}

export async function createFamily(name: string, signal?: AbortSignal): Promise<FamilyCreateResponse> {
  const { data } = await httpClient.post<FamilyCreateResponse>('/api/families', { name }, { signal });
  return data;
}

export async function listFamilyMembers(familyId: number, signal?: AbortSignal): Promise<FamilyMembershipSummary[]> {
  const { data } = await httpClient.get<FamilyMembershipSummary[]>(`/api/families/${familyId}/members`, { signal });
  return data;
}

/** 1f (나 프로필) / 2z (프로필 편집) — the caller's own Account plus its
 *  server-derived AuthorizedFamilySet. */
export async function getMe(signal?: AbortSignal): Promise<MeResponse> {
  const { data } = await httpClient.get<MeResponse>('/api/me', { signal });
  return data;
}

/** 2z (프로필 편집) — self-service only; every field is optional and applies
 *  to the caller's own Account. */
export async function updateMe(body: MeUpdateRequest): Promise<MeResponse> {
  const { data } = await httpClient.patch<MeResponse>('/api/me', body);
  return data;
}

/** 2z (프로필 편집, 가족 내 역할) — self-service relationship label on the
 *  caller's own Membership only; never `status`. */
export async function updateMyMembershipRelationship(
  familyId: number,
  relationship: string,
): Promise<FamilyMembershipSummary> {
  const { data } = await httpClient.patch<FamilyMembershipSummary>(
    `/api/families/${familyId}/members/me`,
    { relationship },
  );
  return data;
}
