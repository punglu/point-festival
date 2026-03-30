import { create } from 'zustand';

interface AuthState {
  token: string | null;
  player: { id: number; name: string; role: string } | null;
  isLoggedIn: boolean;
  isAdmin: boolean;
  setLogin: (token: string, player: { id: number; name: string; role: string }, isAdmin: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  player: null,
  isLoggedIn: false,
  isAdmin: false,

  setLogin: (token, player, isAdmin) => {
    sessionStorage.setItem('accessToken', token);
    set({ token, player, isLoggedIn: true, isAdmin });
  },

  logout: () => {
    sessionStorage.removeItem('accessToken');
    localStorage.removeItem('loggedInPlayer');
    localStorage.removeItem('rememberMe');
    set({ token: null, player: null, isLoggedIn: false, isAdmin: false });
  },
}));
