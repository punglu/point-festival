/** Reward Catalog API client (W7.5 Phase D, SLICE-REWARD-CATALOG, canonical `1l`/`2h`/`2j`). */
import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

type Schemas = components['schemas'];

export type RewardCatalogItem = Schemas['RewardOut'];
export type RewardRedemption = Schemas['RedemptionOut'];

export async function listRewards(familyId: number, signal?: AbortSignal): Promise<RewardCatalogItem[]> {
  const { data } = await httpClient.get<RewardCatalogItem[]>(`/api/families/${familyId}/rewards`, { signal });
  return data;
}

export async function redeemReward(familyId: number, rewardId: number, idempotencyKey: string): Promise<RewardRedemption> {
  const { data } = await httpClient.post<RewardRedemption>(`/api/families/${familyId}/rewards/${rewardId}/redeem`, {
    idempotency_key: idempotencyKey,
  });
  return data;
}
