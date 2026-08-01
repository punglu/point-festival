/**
 * Wagle Target API client — real rooms and messages.
 *
 * This replaces the preview fixtures the Wagle screen rendered through Wave 5.
 * The fixtures stay in the tree only as the design reference they always were;
 * nothing in the production path may fall back to them, because a screen that
 * silently renders sample conversations when the API fails is worse than one
 * that says it failed.
 *
 * **The durable history is the source of truth.** The realtime channel carries
 * identifiers only, so every message body on screen came from these endpoints.
 * That is deliberate: one fetch path means a live message and a recovered one
 * cannot render differently, which is otherwise a bug class that only appears
 * after a network blip.
 */
import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

type Schemas = components['schemas'];

export type WagleRoom = Schemas['RoomResponse'];
export type WagleRoomSummary = Schemas['RoomSummaryResponse'];
export type WagleMessage = Schemas['MessageResponse'];
export type WagleMessageList = Schemas['MessageListResponse'];
export type WagleReadState = Schemas['ReadStateResponse'];

/**
 * Message types the server emits. `SERVICE_ACTION` is a Markpoint system
 * message published by a ServicePrincipal — it must never be rendered as if a
 * person sent it, which is why the UI branches on this rather than on whether
 * a sender name happens to be present.
 */
export type WagleMessageType = 'TEXT' | 'SYSTEM' | 'SERVICE_ACTION';

export async function listRoomSummaries(familyId: number, signal?: AbortSignal) {
  const { data } = await httpClient.get<WagleRoomSummary[]>(
    `/api/families/${familyId}/wagle/room-summaries`,
    { signal },
  );
  return data;
}

export async function listRooms(familyId: number, signal?: AbortSignal) {
  const { data } = await httpClient.get<WagleRoom[]>(`/api/families/${familyId}/wagle/rooms`, {
    signal,
  });
  return data;
}

export interface MessagePage {
  messages: WagleMessage[];
  /** Highest sequence in this page, or 0 — used to prime the realtime cursor
   *  so a reconnect does not re-emit history the screen already rendered. */
  highestSequence: number;
}

export async function listMessages(
  familyId: number,
  roomId: string,
  options: { afterSequence?: number; beforeSequence?: number; limit?: number } = {},
  signal?: AbortSignal,
): Promise<MessagePage> {
  const params: Record<string, number> = {};
  if (options.afterSequence !== undefined) params.after_sequence = options.afterSequence;
  if (options.beforeSequence !== undefined) params.before_sequence = options.beforeSequence;
  if (options.limit !== undefined) params.limit = options.limit;

  const { data } = await httpClient.get<WagleMessageList>(
    `/api/families/${familyId}/wagle/rooms/${roomId}/messages`,
    { params, signal },
  );
  const messages = (data.items ?? []) as WagleMessage[];
  return {
    messages,
    highestSequence: messages.reduce((max, m) => Math.max(max, m.sequence ?? 0), 0),
  };
}

export async function sendMessage(
  familyId: number,
  roomId: string,
  body: { body: string; client_message_id: string },
) {
  const { data } = await httpClient.post<WagleMessage>(
    `/api/families/${familyId}/wagle/rooms/${roomId}/messages`,
    body,
  );
  return data;
}

export async function readState(familyId: number, roomId: string, lastReadSequence?: number) {
  if (lastReadSequence === undefined) {
    const { data } = await httpClient.get<WagleReadState>(
      `/api/families/${familyId}/wagle/rooms/${roomId}/read-state`,
    );
    return data;
  }
  const { data } = await httpClient.put<WagleReadState>(
    `/api/families/${familyId}/wagle/rooms/${roomId}/read-state`,
    { last_read_sequence: lastReadSequence },
  );
  return data;
}

/**
 * The durable recovery endpoint.
 *
 * Called on reconnect and whenever the client detects a sequence gap. It is
 * safe to call with a cursor already covered — replay is expected, and the
 * client deduplicates on message id.
 */
export interface ResumeResult {
  family_id: number;
  room_id: string;
  from_sequence: number;
  next_sequence: number;
  room_next_sequence: number;
  events: {
    event_id: string;
    event_type: string;
    family_id: number;
    room_id: string;
    message_id: string;
    room_sequence: number;
    occurred_at: string;
    actor_type: string;
  }[];
  has_more: boolean;
}

export async function resumeRoom(
  familyId: number,
  roomId: string,
  afterSequence: number,
  signal?: AbortSignal,
) {
  const { data } = await httpClient.get<ResumeResult>(
    `/api/families/${familyId}/wagle/rooms/${roomId}/resume`,
    { params: { after_sequence: afterSequence }, signal },
  );
  return data;
}
