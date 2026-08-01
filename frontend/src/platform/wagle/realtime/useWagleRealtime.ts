/**
 * React binding for the Wagle realtime client.
 *
 * Owns the client's lifetime and exposes only what a screen needs: the
 * connection state, and a way to subscribe a room. It deliberately does not
 * expose the socket — a component that could send frames directly would be
 * able to bypass the cursor bookkeeping that makes reconnects safe.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import {
  buildRealtimeUrl,
  WagleRealtimeClient,
  type RoomKey,
  type WagleConnectionState,
  type WagleRealtimeEvent,
} from './wagleRealtimeClient';

export interface UseWagleRealtimeOptions {
  /** Rooms to keep subscribed. Changing this set re-subscribes incrementally. */
  rooms: RoomKey[];
  enabled?: boolean;
  /** Called when a gap is detected and the room's history must be refetched. */
  onGap?: (familyId: number, roomId: string, fromSequence: number) => void;
  onEvents?: (familyId: number, roomId: string, events: WagleRealtimeEvent[]) => void;
}

export interface UseWagleRealtimeResult {
  state: WagleConnectionState;
  /** Rooms whose authority was withdrawn while connected. */
  revokedRooms: string[];
  primeCursor: (familyId: number, roomId: string, sequence: number) => void;
}

export function useWagleRealtime(options: UseWagleRealtimeOptions): UseWagleRealtimeResult {
  const { rooms, enabled = true, onGap, onEvents } = options;
  const [state, setState] = useState<WagleConnectionState>('idle');
  const [revokedRooms, setRevokedRooms] = useState<string[]>([]);
  const clientRef = useRef<WagleRealtimeClient | null>(null);

  // Handlers are held in a ref so a re-render with a new closure does not tear
  // down and rebuild the socket — reconnecting on every render would look like
  // a flapping network to the user and would replay resume traffic each time.
  const handlerRef = useRef({ onGap, onEvents });
  handlerRef.current = { onGap, onEvents };

  const roomSignature = useMemo(
    () => rooms.map((r) => `${r.familyId}:${r.roomId}`).sort().join(','),
    [rooms],
  );

  useEffect(() => {
    if (!enabled) return undefined;

    const client = new WagleRealtimeClient(
      buildRealtimeUrl(import.meta.env.VITE_API_BASE_URL),
      () => sessionStorage.getItem('accessToken'),
      {
        onState: setState,
        onEvents: (familyId, roomId, events) =>
          handlerRef.current.onEvents?.(familyId, roomId, events),
        onGap: (familyId, roomId, fromSequence) =>
          handlerRef.current.onGap?.(familyId, roomId, fromSequence),
        onSubscriptionRevoked: (familyId, roomId) =>
          setRevokedRooms((prev) => {
            const key = roomId ? `${familyId}:${roomId}` : `${familyId}:*`;
            return prev.includes(key) ? prev : [...prev, key];
          }),
      },
    );
    clientRef.current = client;
    client.connect();

    return () => {
      client.disconnect();
      clientRef.current = null;
    };
    // `enabled` only. The room set is applied by the effect below so that
    // adding a room does not drop the connection.
  }, [enabled]);

  useEffect(() => {
    const client = clientRef.current;
    if (!client) return;
    for (const room of rooms) {
      client.subscribe(room.familyId, room.roomId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roomSignature]);

  const primeCursor = useCallback((familyId: number, roomId: string, sequence: number) => {
    clientRef.current?.primeCursor(familyId, roomId, sequence);
  }, []);

  return { state, revokedRooms, primeCursor };
}
