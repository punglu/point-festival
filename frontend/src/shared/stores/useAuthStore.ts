import { create } from 'zustand';
import type { AdminLoginResponse } from '../../pages/Auth/api/authApi';

interface AuthState {
  token: string | null;
  player: { id: number; name: string; role: string } | null;
  isLoggedIn: boolean;
  isAdmin: boolean;
  adminDisplayName: string | null;
  adminPlayerId: number | null;
  /**
   * MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001.
   *
   * True when the stored token is an **Account-native** Session (`role:
   * "account"`), false for a legacy MarkPoint player/admin token.
   *
   * Every Target screen needs this. The two token kinds are both JWTs in
   * `sessionStorage` and both make `isLoggedIn` true, so without this flag a
   * legacy-signed-in user reaches the Target routes and receives a wall of
   * 401/403 that reads like a broken app rather than "this feature needs the
   * new sign-in".
   */
  isAccountSession: boolean;
  accountId: number | null;
  accountDisplayName: string | null;
  setLogin: (token: string, player: { id: number; name: string; role: string }, isAdmin: boolean) => void;
  adminLogin: (response: AdminLoginResponse) => void;
  accountLogin: (result: { access_token: string; account_id: number; display_name: string }) => void;
  logout: () => void;
}

type RestoredAuth = Pick<
  AuthState,
  'token' | 'isLoggedIn' | 'isAdmin' | 'player' | 'adminDisplayName' | 'adminPlayerId'
  | 'isAccountSession' | 'accountId' | 'accountDisplayName'
>;

const EMPTY_AUTH: RestoredAuth = {
  token: null, isLoggedIn: false, isAdmin: false, player: null,
  adminDisplayName: null, adminPlayerId: null,
  isAccountSession: false, accountId: null, accountDisplayName: null,
};

function restoreFromStorage(): RestoredAuth {
  const token = sessionStorage.getItem('accessToken');
  if (!token) return EMPTY_AUTH;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    // The Account token carries `role: "account"`; a legacy token carries
    // "player" or "admin". Reading the claim is what keeps the two apart —
    // both are otherwise just a JWT in the same storage key.
    if (payload.role === 'account') {
      return {
        ...EMPTY_AUTH,
        token,
        isLoggedIn: true,
        isAccountSession: true,
        accountId: Number(payload.sub),
        accountDisplayName: payload.name ?? null,
      };
    }
    const isAdmin = payload.role === 'admin';
    const player = isAdmin
      ? null
      : { id: Number(payload.sub), name: payload.name ?? '', role: 'player' };
    return {
      ...EMPTY_AUTH,
      token, isLoggedIn: true, isAdmin, player,
      adminDisplayName: isAdmin ? (payload.name ?? null) : null,
      adminPlayerId: isAdmin ? (payload.player_id ?? null) : null,
    };
  } catch {
    sessionStorage.removeItem('accessToken');
    return EMPTY_AUTH;
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  ...restoreFromStorage(),

  setLogin: (token, player, isAdmin) => {
    sessionStorage.setItem('accessToken', token);
    set({ token, player, isLoggedIn: true, isAdmin, adminPlayerId: null });
  },

  accountLogin: (result) => {
    sessionStorage.setItem('accessToken', result.access_token);
    set({
      token: result.access_token,
      isLoggedIn: true,
      isAccountSession: true,
      accountId: result.account_id,
      accountDisplayName: result.display_name,
      isAdmin: false,
      player: null,
      adminDisplayName: null,
      adminPlayerId: null,
    });
  },

  adminLogin: (response) => {
    sessionStorage.setItem('accessToken', response.access_token);
    set({
      isLoggedIn: true,
      isAdmin: true,
      token: response.access_token,
      adminDisplayName: response.display_name,
      adminPlayerId: response.player_id ?? null,
      player: null,
    });
  },

  logout: () => {
    sessionStorage.removeItem('accessToken');
    localStorage.removeItem('loggedInPlayer');
    localStorage.removeItem('rememberMe');
    set({ ...EMPTY_AUTH });
  },
}));
