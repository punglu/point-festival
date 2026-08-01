/**
 * Client for the personal Wagle device endpoints: screen-lock PIN and Push.
 *
 * Both are keyed on a **device identifier**, not on the Family. One personal
 * PIN and one Push subscription per browser installation cover every Family
 * that Account can reach; a per-Family variant would leak a personal device
 * setting into family-visible state.
 *
 * The device id is generated once and kept in `localStorage` rather than
 * `sessionStorage`: it has to survive a tab close, or every new tab would look
 * like a new device and accumulate Push subscriptions and PIN rows.
 */
import { httpClient } from '../../../shared/api/httpClient';

const DEVICE_ID_KEY = 'mongle.wagle.deviceId';

export function wagleDeviceId(): string {
  const existing = localStorage.getItem(DEVICE_ID_KEY);
  if (existing) return existing;
  const generated =
    typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : `dev-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  localStorage.setItem(DEVICE_ID_KEY, generated);
  return generated;
}

export interface DevicePinStatus {
  configured: boolean;
  locked: boolean;
  locked_until: string | null;
  remaining_attempts: number | null;
  pin_version: number | null;
}

export async function getDevicePinStatus(): Promise<DevicePinStatus> {
  const { data } = await httpClient.get<DevicePinStatus>('/api/me/wagle/device-pin', {
    params: { device_id: wagleDeviceId() },
  });
  return data;
}

export async function setDevicePin(pin: string): Promise<DevicePinStatus> {
  const { data } = await httpClient.put<DevicePinStatus>('/api/me/wagle/device-pin', {
    device_id: wagleDeviceId(),
    pin,
  });
  return data;
}

export async function verifyDevicePin(pin: string): Promise<{ unlocked: boolean }> {
  const { data } = await httpClient.post('/api/me/wagle/device-pin/verify', {
    device_id: wagleDeviceId(),
    pin,
  });
  return data;
}

/** Recovery is replacement. There is no endpoint that reads a PIN back. */
export async function resetDevicePin(newPin: string): Promise<DevicePinStatus> {
  const { data } = await httpClient.post<DevicePinStatus>('/api/me/wagle/device-pin/reset', {
    device_id: wagleDeviceId(),
    pin: newPin,
  });
  return data;
}

export async function disableDevicePin(pin: string): Promise<DevicePinStatus> {
  const { data } = await httpClient.post<DevicePinStatus>('/api/me/wagle/device-pin/disable', {
    device_id: wagleDeviceId(),
    pin,
  });
  return data;
}

export async function getRealtimeContext(): Promise<{
  account_id: number;
  authorized_family_ids: number[];
}> {
  const { data } = await httpClient.get('/api/me/wagle/realtime-context');
  return data;
}

function urlBase64ToUint8Array(base64: string): Uint8Array {
  const padding = '='.repeat((4 - (base64.length % 4)) % 4);
  const normalized = (base64 + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = window.atob(normalized);
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
}

/**
 * Register this browser for Web Push.
 *
 * Returns `null` rather than throwing when the browser cannot subscribe, when
 * the user declines, or when no VAPID key is configured. Push is a background
 * convenience: failing to get it must never block entering Wagle, and every
 * message remains recoverable from the durable history regardless.
 */
export async function registerPushSubscription(vapidPublicKey?: string): Promise<boolean> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return false;
  if (!vapidPublicKey) return false;
  try {
    const registration = await navigator.serviceWorker.ready;
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') return false;

    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
    });
    const json = subscription.toJSON() as { endpoint?: string; keys?: Record<string, string> };
    if (!json.endpoint || !json.keys?.p256dh || !json.keys?.auth) return false;

    await httpClient.post('/api/me/wagle/push-subscriptions', {
      device_id: wagleDeviceId(),
      endpoint: json.endpoint,
      p256dh_key: json.keys.p256dh,
      auth_secret: json.keys.auth,
    });
    return true;
  } catch {
    return false;
  }
}

/** Withdraw this device's Push authority — logout, unlink, account switch. */
export async function revokePushSubscription(): Promise<void> {
  try {
    await httpClient.delete(`/api/me/wagle/push-subscriptions/${encodeURIComponent(wagleDeviceId())}`);
  } catch {
    // Best effort. The server also revokes on logout and device unlink, so a
    // failure here is not a lingering capability.
  }
}
