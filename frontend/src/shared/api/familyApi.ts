import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

/** Generated wire types stay at this API boundary. */
export type FamilyRole = components['schemas']['RoleSummary'];
export type FamilyMembershipSummary = components['schemas']['MembershipSummary'];
export type FamilyContextStatus = components['schemas']['ServiceSubscriptionSummary']['status'];
export type FamilyServiceSummary = components['schemas']['ServiceSubscriptionSummary'];
export type AccountFamilyContext = components['schemas']['AccountContextResponse'];

export async function getAccountFamilyContext(signal?: AbortSignal): Promise<AccountFamilyContext> {
  const { data } = await httpClient.get<AccountFamilyContext>('/api/account-context', { signal });
  return data;
}
