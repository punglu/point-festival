/*
 * Mongle service worker — Wagle background Push only.
 *
 * MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001.
 *
 * Scope is deliberately minimal. This worker does no caching, no offline
 * shell and no request interception: those are separate decisions with their
 * own failure modes, and none of them is approved. It handles two events.
 *
 * **The notification shows no message content.** `D6-P1` — how much of a
 * message body a notification may disclose — is undecided, and the server
 * sends identifiers only. A notification renders on a lock screen, outside the
 * app's authentication context, which is exactly why that decision exists. If
 * a payload ever arrives carrying a body, this worker still does not display
 * it; the policy is enforced on both ends rather than trusted from one.
 *
 * **A notification click navigates; it does not authorize.** The click opens
 * the event's own Family and room, and the app then loads that room through
 * the authenticated API, which re-checks Session, Account state, membership,
 * family scope and room permission. If authority is gone the user sees an
 * inaccessible state rather than data — decided by the server, never here.
 */

self.addEventListener('push', (event) => {
  let payload = {};
  try {
    payload = event.data ? event.data.json() : {};
  } catch {
    payload = {};
  }

  const familyId = payload.family_id;
  const roomId = payload.room_id;
  const isService = payload.actor_type === 'SERVICE';

  // Generic, content-free copy. Distinguishing a service notice from a human
  // message is allowed — it is not message content, and the two must never
  // look alike — but no body, sender name or room title appears.
  const title = '몽글';
  const body = isService ? '새로운 알림이 도착했어요' : '새로운 메시지가 도착했어요';

  event.waitUntil(
    self.registration.showNotification(title, {
      body,
      icon: '/favicon-192x192.png',
      badge: '/favicon-32x32.png',
      // Collapse per room so a burst does not stack into a wall of
      // notifications. Bundling *policy* is D6-P3 and undecided; this is only
      // the platform's own replace-by-tag behaviour, not a batching rule.
      tag: roomId ? `wagle-room-${roomId}` : 'wagle',
      renotify: false,
      data: { familyId, roomId, messageId: payload.message_id },
    }),
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const { familyId, roomId } = event.notification.data || {};

  // Land on the event's own Family, not on whatever the app last had open.
  // The target is a plain in-app route; the app re-authorizes on arrival.
  const target =
    familyId && roomId
      ? `/wagle?family=${encodeURIComponent(familyId)}&room=${encodeURIComponent(roomId)}`
      : '/wagle';

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if ('focus' in client) {
          client.postMessage({ type: 'wagle-deeplink', familyId, roomId });
          return client.focus();
        }
      }
      return self.clients.openWindow(target);
    }),
  );
});
