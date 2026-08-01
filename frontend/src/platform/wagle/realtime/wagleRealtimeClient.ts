/**
 * Wagle realtime client: connect, subscribe, reconnect, resume, deduplicate.
 *
 * The one rule everything else follows from: **the server's durable sequence is
 * the truth, the socket is a hint.** Every event that arrives over the wire is
 * an identifier, not content, and the client's job is to notice a gap and go
 * ask the API to fill it. That is why there is no message body anywhere in this
 * file — a transport that carried content would become a second source of truth
 * that can disagree with the first.
 *
 * What this deliberately does not do:
 *
 * - It does not treat a socket send, an ACK, or a delivered event as a
 *   user-facing `DELIVERED` state. That presentation needs separate PM approval
 *   and is out of scope.
 * - It does not subscribe only to the active Family. `ActiveFamilyContext` is a
 *   UI convenience; the authorized set comes from the server and the client
 *   subscribes across all of it.
 * - It does not decide who may see a room. It asks; the server answers. A
 *   `subscribe_denied` is recorded and the other subscriptions carry on.
 */

export type WagleConnectionState =
  | 'idle'
  | 'connecting'
  | 'connected'
  | 'recovering'
  | 'offline'
  | 'authorization_lost';

export interface WagleRealtimeEvent {
  event_id: string;
  event_type: string;
  family_id: number;
  room_id: string;
  message_id: string;
  room_sequence: number;
  occurred_at: string;
  actor_type: string;
}

export interface RoomKey {
  familyId: number;
  roomId: string;
}

export interface WagleRealtimeHandlers {
  onState?: (state: WagleConnectionState) => void;
  /** Called with events already deduplicated and in ascending room sequence. */
  onEvents?: (familyId: number, roomId: string, events: WagleRealtimeEvent[]) => void;
  /**
   * A gap was detected: the client saw sequence N but expected N-1 and does
   * not have it. The host is expected to refetch that room's history.
   */
  onGap?: (familyId: number, roomId: string, fromSequence: number) => void;
  onSubscriptionRevoked?: (familyId: number, roomId?: string) => void;
}

/** Close code the gateway uses for "this credential cannot open the channel". */
const UNAUTHORIZED_CLOSE_CODE = 4401;
const RECONNECT_BASE_MS = 500;
const RECONNECT_MAX_MS = 15000;

function roomKey(familyId: number, roomId: string): string {
  return `${familyId}:${roomId}`;
}

export class WagleRealtimeClient {
  private socket: WebSocket | null = null;
  private state: WagleConnectionState = 'idle';
  private rooms = new Map<string, RoomKey>();
  /** Highest contiguous sequence this client has accepted, per room. */
  private cursors = new Map<string, number>();
  /** Every message id already surfaced, so a replay renders once. */
  private seen = new Map<string, Set<string>>();
  private reconnectAttempt = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private closedByCaller = false;
  /** Set when the server says this credential can never open the channel. */
  private unauthorized = false;

  constructor(
    private readonly url: string,
    private readonly getToken: () => string | null,
    private readonly handlers: WagleRealtimeHandlers = {},
  ) {}

  getState(): WagleConnectionState {
    return this.state;
  }

  /** The client's durable position. Survives reconnects; it is what resume asks from. */
  cursorFor(familyId: number, roomId: string): number {
    return this.cursors.get(roomKey(familyId, roomId)) ?? 0;
  }

  /**
   * Seed the cursor from history the host already loaded.
   *
   * Without this, a client that rendered 40 messages from the REST API would
   * reconnect and resume from 0, re-emitting all 40 as "new".
   */
  primeCursor(familyId: number, roomId: string, sequence: number): void {
    const key = roomKey(familyId, roomId);
    this.cursors.set(key, Math.max(sequence, this.cursors.get(key) ?? 0));
  }

  connect(): void {
    this.closedByCaller = false;
    this.unauthorized = false;
    const token = this.getToken();
    if (!token) {
      this.setState('authorization_lost');
      return;
    }
    this.setState(this.reconnectAttempt === 0 ? 'connecting' : 'recovering');

    const socket = new WebSocket(`${this.url}?token=${encodeURIComponent(token)}`);
    this.socket = socket;

    socket.onopen = () => {
      this.reconnectAttempt = 0;
      this.setState('connected');
      // Re-subscribe every room this client had, each with the cursor it
      // reached. A reconnect must restore the whole subscription set, not just
      // whatever the UI happens to be showing.
      for (const { familyId, roomId } of this.rooms.values()) {
        this.send({
          action: 'subscribe',
          family_id: familyId,
          room_id: roomId,
          after_sequence: this.cursorFor(familyId, roomId),
        });
        this.send({
          action: 'resume',
          family_id: familyId,
          room_id: roomId,
          after_sequence: this.cursorFor(familyId, roomId),
        });
      }
    };

    socket.onmessage = (raw) => {
      let frame: Record<string, unknown>;
      try {
        frame = JSON.parse(raw.data as string);
      } catch {
        return;
      }
      this.handleFrame(frame);
    };

    socket.onclose = (event) => {
      this.socket = null;
      if (this.closedByCaller) {
        this.setState('idle');
        return;
      }
      // 4401 is this gateway's "your credential cannot open this channel".
      // Retrying cannot change that answer, and backing off forever would
      // still mean a reconnect every 15s from every such browser — a
      // self-inflicted load source that also hides the real problem from the
      // user. Settle into `authorization_lost` and stop.
      if (event.code === UNAUTHORIZED_CLOSE_CODE || this.unauthorized) {
        this.setState('authorization_lost');
        return;
      }
      this.setState('offline');
      this.scheduleReconnect();
    };

    socket.onerror = () => {
      // `onclose` always follows, and it owns the reconnect. Reconnecting here
      // too would open two sockets for one failure.
    };
  }

  disconnect(): void {
    this.closedByCaller = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
    this.socket?.close();
    this.socket = null;
    this.setState('idle');
  }

  subscribe(familyId: number, roomId: string): void {
    this.rooms.set(roomKey(familyId, roomId), { familyId, roomId });
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.send({
        action: 'subscribe',
        family_id: familyId,
        room_id: roomId,
        after_sequence: this.cursorFor(familyId, roomId),
      });
    }
  }

  unsubscribe(familyId: number, roomId: string): void {
    const key = roomKey(familyId, roomId);
    this.rooms.delete(key);
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.send({ action: 'unsubscribe', family_id: familyId, room_id: roomId });
    }
  }

  private send(payload: Record<string, unknown>): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(payload));
    }
  }

  private setState(next: WagleConnectionState): void {
    if (this.state === next) return;
    this.state = next;
    this.handlers.onState?.(next);
  }

  private scheduleReconnect(): void {
    // Exponential backoff with a ceiling. A device coming back from sleep
    // should retry quickly; a server that is down should not be hammered.
    const delay = Math.min(RECONNECT_BASE_MS * 2 ** this.reconnectAttempt, RECONNECT_MAX_MS);
    this.reconnectAttempt += 1;
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }

  private handleFrame(frame: Record<string, unknown>): void {
    switch (frame.type) {
      case 'connected':
        this.unauthorized = false;
        this.setState('connected');
        break;

      case 'error':
        if (frame.code === 'unauthorized') {
          // The close frame follows; remember why, so `onclose` does not read
          // it as a network blip and start reconnecting.
          this.unauthorized = true;
          this.setState('authorization_lost');
        }
        break;

      case 'event':
        this.ingest([frame as unknown as WagleRealtimeEvent]);
        break;

      case 'resume': {
        const events = (frame.events as WagleRealtimeEvent[]) ?? [];
        this.ingest(events);
        if (frame.has_more) {
          // Page rather than skip: a client that slept through more than one
          // batch must walk the whole gap, or it just moved the gap along.
          this.send({
            action: 'resume',
            family_id: frame.family_id,
            room_id: frame.room_id,
            after_sequence: frame.next_sequence,
          });
        }
        break;
      }

      case 'subscribe_denied':
      case 'resume_denied':
        this.handlers.onSubscriptionRevoked?.(
          frame.family_id as number,
          frame.room_id as string | undefined,
        );
        break;

      case 'subscription_revoked': {
        const familyId = frame.family_id as number;
        const roomId = frame.room_id as string | undefined;
        if (roomId) {
          this.rooms.delete(roomKey(familyId, roomId));
        } else {
          // Only this family goes. The socket and every other family stay —
          // losing one membership is not a logout.
          for (const [key, value] of [...this.rooms]) {
            if (value.familyId === familyId) this.rooms.delete(key);
          }
        }
        this.handlers.onSubscriptionRevoked?.(familyId, roomId);
        break;
      }

      case 'session_revoked':
        this.closedByCaller = true;
        this.setState('authorization_lost');
        this.socket?.close();
        break;

      default:
        break;
    }
  }

  /**
   * Deduplicate, order, detect gaps, advance the cursor.
   *
   * At-least-once delivery makes duplicates routine, not exceptional: the
   * dispatcher retries, a resume overlaps what the socket already sent, and a
   * reconnect replays. Filtering on `message_id` is what makes all three
   * harmless.
   */
  private ingest(events: WagleRealtimeEvent[]): void {
    if (events.length === 0) return;
    const byRoom = new Map<string, WagleRealtimeEvent[]>();
    for (const event of events) {
      const key = roomKey(event.family_id, event.room_id);
      const seenIds = this.seen.get(key) ?? new Set<string>();
      if (seenIds.has(event.message_id)) continue;
      seenIds.add(event.message_id);
      this.seen.set(key, seenIds);
      const bucket = byRoom.get(key) ?? [];
      bucket.push(event);
      byRoom.set(key, bucket);
    }

    for (const [key, bucket] of byRoom) {
      bucket.sort((a, b) => a.room_sequence - b.room_sequence);
      const { family_id: familyId, room_id: roomId } = bucket[0];
      const cursor = this.cursors.get(key) ?? 0;

      // A jump past the next expected sequence means something was missed. The
      // events are still surfaced — they are real — but the host is told to
      // refetch so the gap is filled from the durable history rather than left
      // as a hole the user would see as missing messages.
      if (bucket[0].room_sequence > cursor + 1) {
        this.handlers.onGap?.(familyId, roomId, cursor);
      }

      this.handlers.onEvents?.(familyId, roomId, bucket);
      this.cursors.set(key, Math.max(cursor, bucket[bucket.length - 1].room_sequence));
    }
  }
}

export function buildRealtimeUrl(apiBase: string | undefined): string {
  const base = apiBase && apiBase.length > 0 ? apiBase : window.location.origin;
  const url = new URL('/api/me/wagle/ws', base);
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  return url.toString();
}
