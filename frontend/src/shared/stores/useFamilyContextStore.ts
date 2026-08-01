import { create } from 'zustand';
import { getAccountFamilyContext, type AccountFamilyContext, type FamilyContextStatus } from '../api/familyApi';
import {
  activeFamilyStorageKey,
  clearActiveFamilySelection,
  resolveActiveFamilyIdWithMigration,
} from '../storage/activeFamilyStorageMigration';

type PlatformFamilyStatus = 'idle' | 'loading' | 'ready' | 'mapping_required' | 'no_available_family' | 'family_selection_required' | 'session_expired' | 'forbidden' | 'backend_unavailable';

interface FamilyContextState {
  context: AccountFamilyContext | null;
  activeFamilyId: number | null;
  status: PlatformFamilyStatus;
  load: () => Promise<void>;
  selectFamily: (familyId: number) => boolean;
  can: (permission: string, familyId?: number | null) => boolean;
  serviceStatus: (serviceCode: string, familyId?: number | null) => FamilyContextStatus | 'unavailable';
  reset: () => void;
}

let requestVersion = 0;

// MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001: this store now
// knows only the canonical key. Carrying the retired key forward — and then
// deleting it — lives entirely in the dedicated migration module, so the
// retired name exists in exactly one place and only as a migration source.
const canonicalStorageKey = activeFamilyStorageKey;

export const useFamilyContextStore = create<FamilyContextState>((set, get) => ({
  context: null,
  activeFamilyId: null,
  status: 'idle',
  load: async () => {
    const version = ++requestVersion;
    set({ status: 'loading' });
    try {
      const context = await getAccountFamilyContext();
      if (version !== requestVersion) return;

      const accessibleFamilyIds = context.families.map((family) => family.id);
      const savedId = resolveActiveFamilyIdWithMigration(context.account_id, accessibleFamilyIds);
      const validSavedId = context.families.some((family) => family.id === savedId) ? savedId : null;
      const activeFamilyId = validSavedId ?? (context.families.length === 1 ? context.families[0].id : null);
      if (activeFamilyId !== null) localStorage.setItem(canonicalStorageKey(context.account_id), String(activeFamilyId));

      set({
        context,
        activeFamilyId,
        status: context.families.length === 0
          ? 'no_available_family'
          : activeFamilyId === null
            ? 'family_selection_required'
            : 'ready',
      });
    } catch (error: unknown) {
      if (version !== requestVersion) return;
      const responseStatus = (error as { response?: { status?: number } }).response?.status;
      const status: PlatformFamilyStatus = responseStatus === 401
        ? 'session_expired'
        : responseStatus === 403
          ? 'mapping_required'
          : responseStatus && responseStatus >= 400 && responseStatus < 500
            ? 'forbidden'
            : 'backend_unavailable';
      set({ context: null, activeFamilyId: null, status });
    }
  },
  selectFamily: (familyId) => {
    const context = get().context;
    const selected = context?.families.find((family) => family.id === familyId);
    if (!context || !selected) return false;
    localStorage.setItem(canonicalStorageKey(context.account_id), String(familyId));
    set({ activeFamilyId: familyId, status: 'ready' });
    return true;
  },
  can: (permission, familyId) => {
    const selected = familyId ?? get().activeFamilyId;
    const family = get().context?.families.find((candidate) => candidate.id === selected);
    return family?.permissions.includes(permission) ?? false;
  },
  serviceStatus: (serviceCode, familyId) => {
    const selected = familyId ?? get().activeFamilyId;
    const family = get().context?.families.find((candidate) => candidate.id === selected);
    return family?.services.find((service) => service.service_code === serviceCode)?.status ?? 'unavailable';
  },
  reset: () => {
    requestVersion += 1;
    const accountId = get().context?.account_id;
    // Explicit logout/reset semantic: clear this account's active-Family
    // selection. Both the canonical and the retired key are removed (see the
    // migration module) so a later login cannot resurrect the pre-logout
    // selection. Only the single already-known accountId is touched — never a
    // wildcard scan, never another account's key.
    if (accountId !== undefined) {
      clearActiveFamilySelection(accountId);
    }
    set({ context: null, activeFamilyId: null, status: 'idle' });
  },
}));
