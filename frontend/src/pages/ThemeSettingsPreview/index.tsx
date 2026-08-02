import { ThemeSettingsScreen, themeSettingsFixture } from '../../screens/family/ThemeSettings';
export function ThemeSettingsPreview() {
  return <ThemeSettingsScreen model={themeSettingsFixture} onBack={() => undefined} onSelectMode={() => undefined} onToggle={() => undefined} />;
}
