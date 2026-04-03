import { useAuthStore } from '../../../shared/stores/useAuthStore';

export function useAdminAuth() {
  const { adminDisplayName, logout } = useAuthStore();
  return { adminDisplayName, logout };
}
