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

// MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001: canonical key going forward.
// `legacyStorageKey` is read-only from this point on (never written to) —
// see `resolveStoredFamilyId` for the exact read-priority/copy-forward rule.
function canonicalStorageKey(accountId: number): string {
  return `mongle.activeFamily.${accountId}`;
}

function legacyStorageKey(accountId: number): string {
  return `naran.activeFamily.${accountId}`;
}

function parseFamilyId(value: string | null): number | null {
  const parsed = value === null ? Number.NaN : Number(value);
  return Number.isInteger(parsed) ? parsed : null;
}

// Read priority (per MONGLE_PWA_AND_STORAGE_MIGRATION_DESIGN.md Option C):
// 1. Canonical key present (even if its value turns out invalid) → canonical
//    is the sole source of truth; legacy is not consulted at all.
// 2. Canonical key absent → fall back to legacy; if legacy holds a value that
//    is both well-formed AND references a Family the current account can
//    still access, copy it forward to the canonical key (one-time) and use
//    it. Legacy is never deleted here, never dual-written, and never
//    overwrites an existing canonical value.
function resolveStoredFamilyId(accountId: number, accessibleFamilyIds: readonly number[]): number | null {
  const canonicalRaw = localStorage.getItem(canonicalStorageKey(accountId));
  if (canonicalRaw !== null) {
    return parseFamilyId(canonicalRaw);
  }

  const legacyId = parseFamilyId(localStorage.getItem(legacyStorageKey(accountId)));
  if (legacyId !== null && accessibleFamilyIds.includes(legacyId)) {
    localStorage.setItem(canonicalStorageKey(accountId), String(legacyId));
    return legacyId;
  }
  return null;
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

      const accessibleFamilyIds = context.families.map((family) => family.id);
      const savedId = resolveStoredFamilyId(context.account_id, accessibleFamilyIds);
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
    // MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001: this is the pre-existing explicit
    // logout/reset semantic (clear the active-Family selection for the current
    // account), now applied to both key names so a subsequent login can't
    // resurrect the pre-logout selection via the legacy-key fallback. Only the
    // single already-known accountId is touched — never a wildcard scan, never
    // another account's key.
    if (accountId !== undefined) {
      localStorage.removeItem(canonicalStorageKey(accountId));
      localStorage.removeItem(legacyStorageKey(accountId));
    }
    set({ context: null, activeFamilyId: null, status: 'idle' });
  },
}));
