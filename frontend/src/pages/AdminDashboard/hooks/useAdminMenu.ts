import { create } from 'zustand';

interface AdminMenuState {
  isMobileOpen: boolean;
  toggleMobile: () => void;
  closeMobile: () => void;
}

export const useAdminMenu = create<AdminMenuState>((set) => ({
  isMobileOpen: false,
  toggleMobile: () => set((s) => ({ isMobileOpen: !s.isMobileOpen })),
  closeMobile: () => set({ isMobileOpen: false }),
}));
