import { httpClient } from './httpClient';

export interface FamilyRole {
  code: string;
  scope_type: 'FAMILY' | 'SERVICE';
  service_code: string | null;
}

export interface FamilyMembershipSummary {
  id: number;
  account_id: number;
  family_group_id: number;
  relationship: string;
  status: string;
  roles: FamilyRole[];
}

export interface AccountFamilyContext {
  account_id: number;
  display_name: string;
  families: Array<{
    id: number;
    name: string;
    status: string;
    membership: FamilyMembershipSummary;
    permissions: string[];
  }>;
}

export async function getAccountFamilyContext(signal?: AbortSignal): Promise<AccountFamilyContext> {
  const { data } = await httpClient.get<AccountFamilyContext>('/api/account-context', { signal });
  return data;
}
