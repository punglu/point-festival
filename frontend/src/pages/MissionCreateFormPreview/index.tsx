import { MissionCreateFormScreen, missionCreateFormFixture } from '../../screens/admin/MissionCreateForm';

export function MissionCreateFormPreview() {
  return <MissionCreateFormScreen model={missionCreateFormFixture} onCancel={() => undefined} onCreate={() => undefined} />;
}
