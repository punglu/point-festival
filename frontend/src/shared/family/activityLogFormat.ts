import type { ActivityLogEntry } from '../api/familyActivityLogApi';
import type { ActivityLogEvent } from '../../screens/family/FamilyActivityLog';

export const ACTION_LABEL: Record<string, string> = {
  'mission.created': '미션 등록',
  'mission.submitted': '미션 제출',
  'mission.approved': '미션 승인',
  'mission.rejected': '미션 반려',
  'mission.reversed': '미션 승인 취소',
  'mission.cancelled': '미션 취소',
  'mission.expired': '미션 기간 만료',
  'points.adjusted': '포인트 조정',
  'points.self_spent': '포인트 사용',
};

export const ACTION_TONE: Record<string, ActivityLogEvent['tone']> = {
  'mission.approved': 'green',
  'mission.rejected': 'red',
  'mission.reversed': 'red',
  'points.adjusted': 'blue',
  'points.self_spent': 'purple',
};

/** `payload` is a free-form dict on the backend (MarkpointAuditEvent.payload); openapi-typescript
 * cannot infer its shape, so it types the field as `Record<string, never>`. Read it defensively
 * rather than trusting a type the generator itself could not actually derive. */
export function toActivityEvent(entry: ActivityLogEntry): ActivityLogEvent {
  const payload = entry.payload as Record<string, unknown>;
  const amount = typeof payload?.amount === 'number' ? payload.amount : null;
  return {
    initial: entry.actor_display_name?.slice(0, 1) ?? '?',
    tone: ACTION_TONE[entry.action] ?? 'purple',
    title: `${entry.actor_display_name ?? '알 수 없음'} · ${ACTION_LABEL[entry.action] ?? entry.action}`,
    detail: amount !== null ? `${amount > 0 ? '+' : ''}${amount}P` : undefined,
    time: new Date(entry.occurred_at).toLocaleTimeString('ko-KR', { hour: 'numeric', minute: '2-digit' }),
  };
}
