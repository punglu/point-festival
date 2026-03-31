import { create } from 'zustand';
import type { AdminLoginResponse } from '../../pages/Auth/api/authApi';

interface AuthState {
  token: string | null;
  player: { id: number; name: string; role: string } | null;
  isLoggedIn: boolean;
  isAdmin: boolean;
  adminDisplayName: string | null;
  setLogin: (token: string, player: { id: number; name: string; role: string }, isAdmin: boolean) => void;
  adminLogin: (response: AdminLoginResponse) => void;
  logout: () => void;
}

function restoreFromStorage(): Pick<AuthState, 'token' | 'isLoggedIn' | 'isAdmin' | 'player' | 'adminDisplayName'> {
  const token = sessionStorage.getItem('accessToken');
  if (!token) return { token: null, isLoggedIn: false, isAdmin: false, player: null, adminDisplayName: null };

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const isAdmin = payload.role === 'admin';
    const player = isAdmin
      ? null
      : { id: Number(payload.sub), name: payload.name ?? '', role: 'player' };
    const adminDisplayName = isAdmin ? (payload.name ?? null) : null;
    return { token, isLoggedIn: true, isAdmin, player, adminDisplayName };
  } catch {
    sessionStorage.removeItem('accessToken');
    return { token: null, isLoggedIn: false, isAdmin: false, player: null, adminDisplayName: null };
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  ...restoreFromStorage(),

  setLogin: (token, player, isAdmin) => {
    sessionStorage.setItem('accessToken', token);
    set({ token, player, isLoggedIn: true, isAdmin });
  },

  adminLogin: (response) => {
    sessionStorage.setItem('accessToken', response.access_token);
    set({
      isLoggedIn: true,
      isAdmin: true,
      token: response.access_token,
      adminDisplayName: response.display_name,
      player: null,
    });
  },

  logout: () => {
    sessionStorage.removeItem('accessToken');
    localStorage.removeItem('loggedInPlayer');
    localStorage.removeItem('rememberMe');
    set({ token: null, player: null, isLoggedIn: false, isAdmin: false, adminDisplayName: null });
  },
}));
