import type { ProfileEditModel } from './types';
export const profileEditFixture: ProfileEditModel = {
  name: '서연',
  colors: [
    { value: '#5A35DF', selected: true },
    { value: '#EF4665', selected: false },
    { value: '#1F9D62', selected: false },
    { value: '#B4791A', selected: false },
  ],
  bio: '오늘도 화이팅! 🌱',
  birthday: '2015. 4. 12',
  familyRole: '자녀',
};
