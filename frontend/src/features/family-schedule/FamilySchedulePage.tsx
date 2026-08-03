import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyScheduleScreen, familyScheduleFixture } from '../../screens/family/FamilySchedule';
import type { ScheduleEvent } from '../../screens/family/FamilySchedule';
import { ScheduleAddScreen, scheduleAddFixture } from '../../screens/family/ScheduleAdd';
import type { ScheduleAddModel } from '../../screens/family/ScheduleAdd';
import { ScheduleDetailScreen } from '../../screens/family/ScheduleDetail';
import { CalendarShareScreen, calendarShareFixture } from '../../screens/family/CalendarShare';
import {
  listScheduleEvents, createScheduleEvent, deleteScheduleEvent,
  type FamilyScheduleEvent,
} from '../../shared/api/familyScheduleApi';
import { listFamilyMembers, type FamilyMembershipSummary } from '../../shared/api/familyApi';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './FamilySchedulePage.module.css';

type View = 'calendar' | 'add' | 'detail' | 'share';

function isSameDay(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

function eventMeta(event: FamilyScheduleEvent, nameByMembershipId: Map<number, string>): string {
  const time = new Date(event.starts_at).toLocaleTimeString('ko-KR', { hour: 'numeric', minute: '2-digit' });
  const attendeeNames = (event.attendee_membership_ids ?? []).map((id) => nameByMembershipId.get(id)).filter(Boolean) as string[];
  const who = attendeeNames.length > 0 ? attendeeNames.join(', ') : '온 가족';
  return [time, event.location, who].filter(Boolean).join(' · ');
}

function toScheduleEvent(event: FamilyScheduleEvent, nameByMembershipId: Map<number, string>): ScheduleEvent {
  const attendeeNames = (event.attendee_membership_ids ?? []).map((id) => nameByMembershipId.get(id)).filter(Boolean) as string[];
  return {
    id: String(event.id),
    color: 'purple',
    title: event.title,
    meta: eventMeta(event, nameByMembershipId),
    people: attendeeNames.length > 0 ? attendeeNames : ['온 가족'],
  };
}

/**
 * `/family/schedule` — canonical 1g (가족 일정, W7.5 Phase D SLICE-SCHEDULE)
 * with 1o (일정 추가)/2u (일정 상세) real, 3a (캘린더 공유) staying fixture.
 *
 * List/create/delete are real. Edit (`1o` reused for editing) is not wired
 * to a real `PATCH` — the flow to get there (`onEdit` from `2u`) reopens the
 * Add screen with the fixture, matching the frozen Screen's own navigation,
 * but this task only wires the create direction since the Add screen's
 * model has no "editing an existing event" state distinct from "creating a
 * new one" in its own type. `3a`'s Google/Apple sync stays fixture: real
 * external-service OAuth/feed integration is out of this Slice's scope.
 */
export function FamilySchedulePage() {
  const navigate = useNavigate();
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const [view, setView] = useState<View>('calendar');
  const [events, setEvents] = useState<FamilyScheduleEvent[] | null>(null);
  const [members, setMembers] = useState<FamilyMembershipSummary[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<FamilyScheduleEvent | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [addForm, setAddForm] = useState<ScheduleAddModel>(scheduleAddFixture);
  const [saving, setSaving] = useState(false);

  const reload = () => {
    if (activeFamilyId === null) return;
    setLoadError(null);
    listScheduleEvents(activeFamilyId).then(setEvents).catch(() => setLoadError('일정을 불러오지 못했어요.'));
  };

  useEffect(() => {
    if (activeFamilyId === null) return undefined;
    const controller = new AbortController();
    setLoadError(null);
    Promise.all([listScheduleEvents(activeFamilyId, controller.signal), listFamilyMembers(activeFamilyId, controller.signal)])
      .then(([eventList, memberList]) => {
        setEvents(eventList);
        setMembers(memberList);
      })
      .catch(() => { if (!controller.signal.aborted) setLoadError('일정을 불러오지 못했어요.'); });
    return () => controller.abort();
  }, [activeFamilyId]);

  const nameByMembershipId = useMemo(() => new Map(members.map((m) => [m.id, m.account_display_name])), [members]);

  const handleSave = async () => {
    if (activeFamilyId === null) return;
    setSaving(true);
    setLoadError(null);
    try {
      const selectedNames = new Set(addForm.attendees.filter((a) => a.selected).map((a) => a.name));
      const attendeeIds = members.filter((m) => selectedNames.has(m.account_display_name)).map((m) => m.id);
      await createScheduleEvent(activeFamilyId, {
        title: addForm.title,
        starts_at: new Date().toISOString(),
        location: addForm.place || null,
        memo: addForm.memo || null,
        attendee_membership_ids: attendeeIds.length > 0 ? attendeeIds : null,
      });
      setAddForm(scheduleAddFixture);
      reload();
      setView('calendar');
    } catch {
      setLoadError('일정을 저장하지 못했어요.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (activeFamilyId === null || selectedEvent === null) return;
    try {
      await deleteScheduleEvent(activeFamilyId, selectedEvent.id);
      reload();
    } catch {
      // A failed delete must never look like a successful one: the event
      // stays in `events` (no reload happened) and the failure surfaces as
      // a real error banner on the calendar view, not a silent no-op.
      setLoadError('일정을 삭제하지 못했어요.');
    } finally {
      setSelectedEvent(null);
      setView('calendar');
    }
  };

  if (view === 'add') {
    return (
      <div className={styles.wrap}>
        <ScheduleAddScreen
          model={{
            ...addForm,
            attendees: members.length > 0 ? members.map((m) => ({ name: m.account_display_name, selected: addForm.attendees.some((a) => a.name === m.account_display_name && a.selected) })) : addForm.attendees,
          }}
          onBack={() => setView('calendar')}
          onSave={() => void handleSave()}
          onChangeField={(field, value) => setAddForm((prev) => ({ ...prev, [field]: value }))}
          onToggleAttendee={(name) =>
            setAddForm((prev) => ({
              ...prev,
              attendees: prev.attendees.some((a) => a.name === name)
                ? prev.attendees.map((a) => (a.name === name ? { ...a, selected: !a.selected } : a))
                : [...prev.attendees, { name, selected: true }],
            }))
          }
        />
        {saving && <p className={styles.status}>저장 중…</p>}
        {!saving && loadError && <p className={styles.error} role="alert">{loadError}</p>}
      </div>
    );
  }

  if (view === 'detail' && selectedEvent) {
    return (
      <div className={styles.wrap}>
        <ScheduleDetailScreen
          model={{
            category: '가족 행사',
            title: selectedEvent.title,
            dateTime: new Date(selectedEvent.starts_at).toLocaleString('ko-KR'),
            place: selectedEvent.location ?? '장소 없음',
            repeat: '반복 없음',
            attendees: (selectedEvent.attendee_membership_ids ?? []).map((id, i) => ({
              name: nameByMembershipId.get(id) ?? `구성원 ${id}`,
              tone: (['blue', 'red', 'purple', 'green'] as const)[i % 4],
            })),
          }}
          onBack={() => setView('calendar')}
          onEdit={() => setView('add')}
          onDelete={() => void handleDelete()}
        />
      </div>
    );
  }

  if (view === 'share') {
    return <div className={styles.wrap}><CalendarShareScreen model={calendarShareFixture} onClose={() => setView('calendar')} /></div>;
  }

  const now = new Date();
  const realEvents = events ?? [];
  const todayEvents = realEvents.filter((e) => isSameDay(new Date(e.starts_at), now)).map((e) => toScheduleEvent(e, nameByMembershipId));
  const upcomingEvents = realEvents
    .filter((e) => new Date(e.starts_at).getTime() > now.getTime() && !isSameDay(new Date(e.starts_at), now))
    .map((e) => toScheduleEvent(e, nameByMembershipId));

  // Loading and load-failure must never show the fixture's fake events
  // (e.g. "가족 저녁 · 삼겹살 파티") -- only real events or a real empty
  // list ever render here.
  const model = {
    ...familyScheduleFixture,
    weekSummary: events === null ? (loadError ?? familyScheduleFixture.weekSummary) : `이번 주 일정 ${realEvents.length}개 · 오늘 ${todayEvents.length}개`,
    todayEvents: events === null ? [] : todayEvents,
    upcomingEvents: events === null ? [] : upcomingEvents,
  };

  const findEventById = (event: ScheduleEvent) => realEvents.find((e) => String(e.id) === event.id) ?? null;

  return (
    <div className={styles.wrap}>
      <FamilyScheduleScreen
        model={model}
        onBack={() => navigate('/family')}
        onAddSchedule={() => setView('add')}
        onSelectEvent={(event) => { setSelectedEvent(findEventById(event)); setView('detail'); }}
      />
      {/* Load failures already surface inline via weekSummary above (events
          stays null). A delete failure happens after events is already
          populated, so it needs its own visible banner here -- otherwise
          the failed delete would look identical to a successful one. */}
      {events !== null && loadError && <p className={styles.error} role="alert">{loadError}</p>}
      <button type="button" className={styles.shareLink} onClick={() => setView('share')}>캘린더 공유</button>
    </div>
  );
}
