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
}

export const authApi = {
  login: async (payload: LoginPayload): Promise<LoginResult> => {
    const { data } = await httpClient.post<LoginResult>('/api/auth/login', payload);
    return data;
  },

  logout: async (): Promise<void> => {
    await httpClient.post('/api/auth/logout');
  },

  getPlayers: async (): Promise<PlayerListItem[]> => {
    const { data } = await httpClient.get<PlayerListItem[]>('/api/players');
    return data;
  },
};
