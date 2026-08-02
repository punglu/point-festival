import { CalendarShareScreen, calendarShareFixture } from '../../screens/family/CalendarShare';
export function CalendarSharePreview() {
  return <CalendarShareScreen model={calendarShareFixture} onClose={() => undefined} onShare={() => undefined} onToggleIntegration={() => undefined} />;
}
