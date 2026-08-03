/** Notification Preferences API client (W7.5 Phase D, SLICE-NOTIFICATION-PREFERENCES, canonical `2n`). */
import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

type Schemas = components['schemas'];

export type NotificationPreferenceEntry = Schemas['PreferenceOut'];

export async function getNotificationPreferences(signal?: AbortSignal): Promise<NotificationPreferenceEntry[]> {
  const { data } = await httpClient.get<NotificationPreferenceEntry[]>('/api/me/notification-preferences', { signal });
  return data;
}

export async function setNotificationPreference(prefKey: string, enabled: boolean): Promise<NotificationPreferenceEntry[]> {
  const { data } = await httpClient.put<NotificationPreferenceEntry[]>('/api/me/notification-preferences', {
    preferences: [{ pref_key: prefKey, enabled }],
  });
  return data;
}
