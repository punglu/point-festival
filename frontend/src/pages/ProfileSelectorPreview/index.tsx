import { ProfileSelectorScreen, profileSelectorFixture } from '../../screens/auth/ProfileSelector';

export function ProfileSelectorPreview() {
  return <ProfileSelectorScreen model={profileSelectorFixture} onSelect={() => undefined} />;
}
