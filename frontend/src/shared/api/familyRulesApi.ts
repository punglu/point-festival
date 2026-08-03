/** Family Rules API client (W7.5 Phase D, SLICE-FAMILY-RULES, canonical `1v`). */
import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

type Schemas = components['schemas'];

export type FamilyRule = Schemas['FamilyRuleOut'];

export async function listRules(familyId: number, signal?: AbortSignal): Promise<FamilyRule[]> {
  const { data } = await httpClient.get<FamilyRule[]>(`/api/families/${familyId}/rules`, { signal });
  return data;
}
