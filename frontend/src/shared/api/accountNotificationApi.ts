/** Account Notification API client (W7.5 Phase D, SLICE-NOTIFICATION-LIST, canonical `1n`). */
import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

type Schemas = components['schemas'];

export type AccountNotification = Schemas['NotificationOut'];

export async function listNotifications(signal?: AbortSignal): Promise<AccountNotification[]> {
  const { data } = await httpClient.get<AccountNotification[]>('/api/me/notifications', { signal });
  return data;
}

export async function markNotificationRead(notificationId: number): Promise<AccountNotification> {
  const { data } = await httpClient.post<AccountNotification>(`/api/me/notifications/${notificationId}/read`);
  return data;
}

export async function markAllNotificationsRead(): Promise<void> {
  await httpClient.post('/api/me/notifications/read-all');
}
