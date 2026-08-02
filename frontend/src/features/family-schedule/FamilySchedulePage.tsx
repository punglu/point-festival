import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyScheduleScreen, familyScheduleFixture } from '../../screens/family/FamilySchedule';
import type { ScheduleEvent } from '../../screens/family/FamilySchedule';
import { ScheduleAddScreen, scheduleAddFixture } from '../../screens/family/ScheduleAdd';
import { ScheduleDetailScreen, scheduleDetailFixture } from '../../screens/family/ScheduleDetail';
import { CalendarShareScreen, calendarShareFixture } from '../../screens/family/CalendarShare';
import styles from './FamilySchedulePage.module.css';

type View = 'calendar' | 'add' | 'detail' | 'share';

/**
 * `/family/schedule` — canonical 1g (가족 일정, CHILD_OF 1b) with 1o/2u/3a as
 * nested views/overlays per the W7.1 Ownership Matrix.
 * frontend/src/features/family-schedule/ was an empty scaffold with no real
 * entry point before this pass.
 */
export function FamilySchedulePage() {
  const navigate = useNavigate();
  const [view, setView] = useState<View>('calendar');
  const [selectedEvent, setSelectedEvent] = useState<ScheduleEvent | null>(null);

  if (view === 'add') {
    return <div className={styles.wrap}><ScheduleAddScreen model={scheduleAddFixture} onBack={() => setView('calendar')} onSave={() => setView('calendar')} /></div>;
  }

  if (view === 'detail' && selectedEvent) {
    return (
      <div className={styles.wrap}>
        <ScheduleDetailScreen
          model={{ ...scheduleDetailFixture, title: selectedEvent.title }}
          onBack={() => setView('calendar')}
          onEdit={() => setView('add')}
          onDelete={() => setView('calendar')}
        />
      </div>
    );
  }

  if (view === 'share') {
    return <div className={styles.wrap}><CalendarShareScreen model={calendarShareFixture} onClose={() => setView('calendar')} /></div>;
  }

  return (
    <div className={styles.wrap}>
      <FamilyScheduleScreen
        model={familyScheduleFixture}
        onBack={() => navigate('/family')}
        onAddSchedule={() => setView('add')}
        onSelectEvent={(event) => { setSelectedEvent(event); setView('detail'); }}
      />
      <button type="button" className={styles.shareLink} onClick={() => setView('share')}>캘린더 공유</button>
    </div>
  );
}
