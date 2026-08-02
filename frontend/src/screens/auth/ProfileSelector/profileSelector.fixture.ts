import type { ProfileSelectorScreenModel } from './types';

export const profileSelectorFixture: ProfileSelectorScreenModel = {
  title: '누가 이용하나요?',
  subtitle: '프로필을 선택하고 PIN 번호를 입력해 주세요',
  profiles: [
    { name: '민준', role: '자녀', initial: '민' },
    { name: '서연', role: '자녀', initial: '서' },
    { name: '엄마', role: '보호자', initial: '엄' },
  ],
};
