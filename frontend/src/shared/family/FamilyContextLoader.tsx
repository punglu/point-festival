import { useEffect } from 'react';
import { useAuthStore } from '../stores/useAuthStore';
import { useFamilyContextStore } from '../stores/useFamilyContextStore';

export function FamilyContextLoader({ children }: { children: React.ReactNode }) {
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn);
  // MONGLE-W7-4-MULTI-FAMILY-ACTIVEFAMILY-PERSISTENCE-REMEDIATION-001: a
  // second `accountLogin`/`setLogin` while already logged in (switching
  // identity without an explicit logout first) leaves `isLoggedIn` at `true`
  // throughout, so it alone never re-triggers this effect -- the family
  // context (including `activeFamilyId`) from the *previous* identity stayed
  // live under the new one. `token` changes on every successful login
  // (a fresh JWT string) regardless of whether `isLoggedIn` itself flips, so
  // including it here is what actually re-runs `load()` for the new identity.
  const token = useAuthStore((state) => state.token);
  const load = useFamilyContextStore((state) => state.load);
  const reset = useFamilyContextStore((state) => state.reset);

  useEffect(() => {
    if (isLoggedIn) void load();
    else reset();
  }, [isLoggedIn, token, load, reset]);

  return <>{children}</>;
}
