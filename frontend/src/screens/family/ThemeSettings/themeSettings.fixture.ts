import type { ThemeSettingsModel } from './types';
export const themeSettingsFixture: ThemeSettingsModel = {
  title: '화면 테마',
  modes: [
    { label: '라이트', selected: true },
    { label: '다크', selected: false },
    { label: '시스템 설정', selected: false },
  ],
  largeText: false,
  highContrast: false,
  fontScale: 50,
  previewText: '가족 플랫폼',
};
