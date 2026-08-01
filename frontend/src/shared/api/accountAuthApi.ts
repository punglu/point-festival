/**
 * Account-native authentication (Wave 1, D2/D3).
 *
 * MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001 added this because the browser
 * had no way to obtain an Account Session at all. The app shipped only the
 * legacy MarkPoint player PIN login, whose token is a *player* credential —
 * every Target route (`/api/account-context`, all of `/api/me/markpoint/*`,
 * the Wagle rooms, the realtime socket) refuses it. So the entire Target UI,
 * fully built and tested on the backend since Wave 1, was unreachable from a
 * browser. This is the missing seam, not a new feature.
 *
 * The refresh token is deliberately **not** stored in `localStorage`. It is a
 * long-lived credential; keeping it in memory means a stolen storage dump does
 * not hand over 30 days of access. The short-lived access token stays in
 * `sessionStorage` alongside the legacy one, because that is where
 * `httpClient` already looks for it.
 */
import { httpClient } from './httpClient';

export interface AccountLoginResult {
  access_token: string;
  refresh_token: string;
  account_id: number;
  display_name: string;
  is_password_change_required: boolean;
}

const DEVICE_ID_KEY = 'mongle.deviceId';

/**
 * A stable per-browser identifier.
 *
 * Kept in `localStorage`, not `sessionStorage`: a device that looked new on
 * every tab would accumulate Sessions and Push subscriptions, and "unlink this
 * device" would never match the device the user meant.
 */
export function deviceId(): string {
  const existing = localStorage.getItem(DEVICE_ID_KEY);
  if (existing) return existing;
  const generated =
    typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : `dev-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  localStorage.setItem(DEVICE_ID_KEY, generated);
  return generated;
}

export async function accountLogin(username: string, password: string) {
  const { data } = await httpClient.post<AccountLoginResult>('/api/auth/account/login', {
    username,
    password,
    device_id: deviceId(),
  });
  return data;
}

export async function accountRefresh(refreshToken: string) {
  const { data } = await httpClient.post<AccountLoginResult>('/api/auth/account/refresh', {
    refresh_token: refreshToken,
  });
  return data;
}

export async function accountLogout() {
  try {
    await httpClient.post('/api/auth/account/logout');
  } catch {
    // Best effort. The local session is cleared by the caller regardless — a
    // failed server call must not leave the user apparently signed in.
  }
}
