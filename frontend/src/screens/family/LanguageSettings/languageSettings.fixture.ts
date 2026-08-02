import type { LanguageSettingsModel } from './types';
export const languageSettingsFixture: LanguageSettingsModel = {
  title: '언어',
  options: [
    { label: '한국어', selected: true },
    { label: 'English', selected: false },
    { label: '日本語', selected: false },
  ],
  notice: '언어를 바꾸면 앱을 재시작해야 적용돼요.',
};
