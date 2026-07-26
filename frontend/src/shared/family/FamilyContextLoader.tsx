import { useEffect } from 'react';
import { useAuthStore } from '../stores/useAuthStore';
import { useFamilyContextStore } from '../stores/useFamilyContextStore';

export function FamilyContextLoader({ children }: { children: React.ReactNode }) {
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn);
  const load = useFamilyContextStore((state) => state.load);
  const reset = useFamilyContextStore((state) => state.reset);

  useEffect(() => {
    if (isLoggedIn) void load();
    else reset();
  }, [isLoggedIn, load, reset]);

  return <>{children}</>;
}
