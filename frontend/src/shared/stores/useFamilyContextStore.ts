import { create } from 'zustand';
import { getAccountFamilyContext, type AccountFamilyContext } from '../api/familyApi';

type FamilyContextStatus = 'idle' | 'loading' | 'ready' | 'mapping_required' | 'error';

interface FamilyContextState {
  context: AccountFamilyContext | null;
  activeFamilyId: number | null;
  status: FamilyContextStatus;
  load: () => Promise<void>;
  selectFamily: (familyId: number | null) => void;
  can: (permission: string, familyId?: number | null) => boolean;
  reset: () => void;
}

const ACTIVE_FAMILY_KEY = 'activeFamilyId';

function savedFamilyId(): number | null {
  const value = sessionStorage.getItem(ACTIVE_FAMILY_KEY);
  return value && Number.isInteger(Number(value)) ? Number(value) : null;
}

export const useFamilyContextStore = create<FamilyContextState>((set, get) => ({
  context: null,
  activeFamilyId: savedFamilyId(),
  status: 'idle',
  load: async () => {
    set({ status: 'loading' });
    try {
      const context = await getAccountFamilyContext();
      const remembered = get().activeFamilyId;
      const activeFamilyId = context.families.some((family) => family.id === remembered)
        ? remembered
        : (context.families[0]?.id ?? null);
      if (activeFamilyId !== null) sessionStorage.setItem(ACTIVE_FAMILY_KEY, String(activeFamilyId));
      set({ context, activeFamilyId, status: 'ready' });
    } catch (error: unknown) {
      const responseStatus = (error as { response?: { status?: number } }).response?.status;
      set({ context: null, activeFamilyId: null, status: responseStatus === 403 ? 'mapping_required' : 'error' });
    }
  },
  selectFamily: (familyId) => {
    if (familyId === null) sessionStorage.removeItem(ACTIVE_FAMILY_KEY);
    else sessionStorage.setItem(ACTIVE_FAMILY_KEY, String(familyId));
    set({ activeFamilyId: familyId });
  },
  can: (permission, familyId) => {
    const selected = familyId ?? get().activeFamilyId;
    const family = get().context?.families.find((candidate) => candidate.id === selected);
    return family?.permissions.includes(permission) ?? false;
  },
  reset: () => {
    sessionStorage.removeItem(ACTIVE_FAMILY_KEY);
    set({ context: null, activeFamilyId: null, status: 'idle' });
  },
}));
