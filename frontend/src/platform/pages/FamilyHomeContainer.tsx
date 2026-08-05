import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FamilyHomeScreen } from '../../screens/family/FamilyHome';
import type { FamilyHomeScreenModel } from '../../screens/family/FamilyHome';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { listActivityLog } from '../../shared/api/familyActivityLogApi';
import { toActivityEvent } from '../../shared/family/activityLogFormat';
import { listNotifications } from '../../shared/api/accountNotificationApi';

const SERVICE_ROUTE: Record<string, string> = {
  markpoint: '/markpoint',
  schedule: '/family/schedule',
  album: '/family/album',
  todo: '/family/todo',
};

/**
 * Product Adapter for canonical Screen 1b (가족 홈), zones 1-4 only. Mounted at
 * the top of `/family`'s "a family is selected" state — every existing real
 * section below it (family switcher, admin/service-admin badges, the 3
 * feature links beyond the 4 tile slots, permission list) is unchanged and
 * unremoved; this only replaces what the frozen canonical visual can
 * genuinely represent, additively.
 *
 * Real-data notes (see this task's own handoff for full reasoning):
 * - "가족 최근 활동" reuses the real `family_activity_log` API (already live
 *   at 2r) rather than the canonical fixture's invented events; entries with
 *   a negative/neutral tone (rejections etc.) are filtered out — the frozen
 *   visual has only 3 positive-shaped tone slots (star/level/gift) and no
 *   red/neutral slot, and the fixture's own 3 example events were themselves
 *   all positive.
 * - The 4-tile grid's "가족 일정"/"앨범"/"할 일" tiles are marked available
 *   (not "준비중") because all three are real, live product features today,
 *   unlike when the mockup was frozen. "포인트 잔치" keeps the frozen
 *   visual's one highlighted/mascot tile slot, with its own "준비중"/이용
 *   불가 state now driven by the real subscription status instead of a
 *   hardcoded `true`.
 * - No real per-user avatar photo or activity-count/unread-count-badge
 *   number exists in the canonical visual's own frozen design beyond a
 *   boolean unread dot, which is wired to a real `GET /api/me/notifications`
 *   check.
 */
export function FamilyHomeContainer({ familyId, familyName }: { familyId: number; familyName: string }) {
  const navigate = useNavigate();
  const accountDisplayName = useAuthStore((s) => s.accountDisplayName);
  const serviceStatus = useFamilyContextStore((s) => s.serviceStatus);
  const [activities, setActivities] = useState<FamilyHomeScreenModel['activities']>([]);
  const [bellUnread, setBellUnread] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    listActivityLog(familyId, controller.signal)
      .then((entries) => {
        if (controller.signal.aborted) return;
        const mapped = entries
          .map(toActivityEvent)
          .filter((event) => event.tone !== 'red')
          .slice(0, 3)
          .map((event) => {
            const isGift = event.tone === 'blue' || event.tone === 'purple';
            const tone: 'gift' | 'star' = isGift ? 'gift' : 'star';
            return {
              tone,
              glyph: isGift ? '♥' : '★',
              title: event.title,
              meta: event.detail ?? '',
              point: Boolean(event.detail),
              time: event.time,
            };
          });
        setActivities(mapped);
      })
      .catch(() => { if (!controller.signal.aborted) setActivities([]); });
    return () => controller.abort();
  }, [familyId]);

  useEffect(() => {
    const controller = new AbortController();
    listNotifications(controller.signal)
      .then((list) => { if (!controller.signal.aborted) setBellUnread(list.some((n) => n.read_at === null)); })
      .catch(() => { if (!controller.signal.aborted) setBellUnread(false); });
    return () => controller.abort();
  }, []);

  const markpointAvailable = serviceStatus('markpoint') === 'active';

  const model: FamilyHomeScreenModel = {
    greetingTitle: `안녕하세요, ${accountDisplayName ?? '회원'}님!`,
    greetingSub: `${familyName}과 함께하는 하루를 응원해요`,
    bellUnread,
    heroTitle: '가족 대화',
    heroBody: ['지금 가족들과', '이야기 나눠보세요'],
    heroCtaLabel: '바로가기',
    activitiesTitle: '가족 최근 활동',
    activitiesMoreLabel: '더보기',
    activities,
    servicesTitle: '우리 서비스',
    services: [
      { id: 'markpoint', label: '포인트 잔치', sub: '다양한 미션과 보상', highlighted: true, available: markpointAvailable, icon: 'markpoint' },
      { id: 'schedule', label: '가족 일정', sub: '소중한 일정을 함께', highlighted: false, available: true, icon: 'schedule' },
      { id: 'album', label: '앨범', sub: '우리의 추억 모아보기', highlighted: false, available: true, icon: 'album' },
      { id: 'todo', label: '할 일', sub: '함께 목표를 관리해요', highlighted: false, available: true, icon: 'todo' },
    ],
  };

  return (
    <FamilyHomeScreen
      model={model}
      onHeroClick={() => navigate('/wagle')}
      onActivityMore={() => navigate('/family/members')}
      onServiceClick={(id) => { const to = SERVICE_ROUTE[id]; if (to) navigate(to); }}
      onBellClick={() => navigate('/family/notifications')}
    />
  );
}
