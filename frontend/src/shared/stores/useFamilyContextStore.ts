import { create } from 'zustand';
import { getAccountFamilyContext, type AccountFamilyContext, type FamilyContextStatus } from '../api/familyApi';

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

function storageKey(accountId: number): string {
  return `naran.activeFamily.${accountId}`;
}

function storedFamilyId(accountId: number): number | null {
  const value = localStorage.getItem(storageKey(accountId));
  const parsed = value === null ? Number.NaN : Number(value);
  return Number.isInteger(parsed) ? parsed : null;
}

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

      const savedId = storedFamilyId(context.account_id);
      const validSavedId = context.families.some((family) => family.id === savedId) ? savedId : null;
      const activeFamilyId = validSavedId ?? (context.families.length === 1 ? context.families[0].id : null);
      if (activeFamilyId !== null) localStorage.setItem(storageKey(context.account_id), String(activeFamilyId));

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
    localStorage.setItem(storageKey(context.account_id), String(familyId));
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
    if (accountId !== undefined) localStorage.removeItem(storageKey(accountId));
    set({ context: null, activeFamilyId: null, status: 'idle' });
  },
}));
