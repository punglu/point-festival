import { httpClient } from '../../../shared/api/httpClient';

interface LoginPayload {
  player_id: number;
  pin: string;
  remember_me: boolean;
}

interface LoginResult {
  access_token: string;
  player_id: number;
  player_name: string;
  player_role: string;
  is_admin: boolean;
  message: string;
}

interface PlayerListItem {
  id: number;
  name: string;
  role: string;
  last_login: number | null;
  is_locked: boolean;
  total_points?: number;
  photo?: string | null;
}

export interface AdminLoginResponse {
  access_token: string;
  token_type: string;
  display_name: string;
  is_admin: boolean;
}

export async function adminLogin(
  username: string,
  password: string,
  signal?: AbortSignal,
): Promise<AdminLoginResponse> {
  const { data } = await httpClient.post<AdminLoginResponse>(
    '/api/auth/admin/login',
    { username, password },
    { signal },
  );
  return data;
}

export const authApi = {
  login: async (payload: LoginPayload, signal?: AbortSignal): Promise<LoginResult> => {
    const { data } = await httpClient.post<LoginResult>('/api/auth/login', payload, { signal });
    return data;
  },

  logout: async (): Promise<void> => {
    await httpClient.post('/api/auth/logout');
  },

  getPlayers: async (signal?: AbortSignal): Promise<PlayerListItem[]> => {
    const { data } = await httpClient.get<PlayerListItem[]>('/api/players', { signal });
    return data;
  },
};
