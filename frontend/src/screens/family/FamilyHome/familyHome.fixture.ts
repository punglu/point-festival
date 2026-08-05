import type { FamilyHomeScreenModel } from './types';

export const familyHomeFixture: FamilyHomeScreenModel = {
  greetingTitle: '안녕하세요, 서연님!',
  greetingSub: '우리 가족의 행복한 하루를 응원해요 💜',
  bellUnread: true,
  heroTitle: '가족 대화',
  heroBody: ['지금 가족들과', '이야기 나눠보세요'],
  heroCtaLabel: '바로가기',
  activitiesTitle: '가족 최근 활동',
  activitiesMoreLabel: '더보기',
  activities: [
    { tone: 'star', glyph: '★', title: '민준이가 "독서 미션"을 완료했어요!', meta: '+200P 획득', point: true, time: '12분 전' },
    { tone: 'level', glyph: '↑', title: '서연이가 Lv.3 모험가가 되었어요!', meta: '레벨업 축하해요 🎉', point: false, time: '1시간 전' },
    { tone: 'gift', glyph: '♥', title: '아빠가 서연이에게 포인트를 선물했어요', meta: '+500P', point: true, time: '3시간 전' },
  ],
  servicesTitle: '우리 서비스',
  services: [
    { id: 'markpoint', label: '포인트 잔치', sub: '다양한 미션과 보상', highlighted: true, available: true, icon: 'markpoint' },
    { id: 'schedule', label: '가족 일정', sub: '소중한 일정을 함께', highlighted: false, available: false, icon: 'schedule' },
    { id: 'album', label: '앨범', sub: '우리의 추억 모아보기', highlighted: false, available: false, icon: 'album' },
    { id: 'todo', label: '할 일', sub: '함께 목표를 관리해요', highlighted: false, available: false, icon: 'todo' },
  ],
};
