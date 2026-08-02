import type { FamilyRulesGuideModel } from './types';
export const familyRulesGuideFixture: FamilyRulesGuideModel = {
  title: '가족 규칙 안내',
  heroTitle: '우리 가족이 함께 지켜요',
  heroBody: '미션·포인트·대화 사용에 대한 우리 가족만의 약속입니다.',
  groups: [
    {
      label: '미션 · 포인트',
      items: [
        { title: '미션 완료는 보호자 승인 후 지급돼요', description: '인증 사진을 정직하게 올려주세요', tone: 'purple' },
        { title: '포인트 차감은 기록으로 남아요', description: '약속을 지키지 못하면 포인트가 줄어들 수 있어요', tone: 'red' },
      ],
    },
    {
      label: '대화 · 앨범',
      items: [
        { title: '서로에게 상냥한 말을 사용해요', description: '가족 대화방은 우리 모두가 함께 보는 공간이에요', tone: 'blue' },
        { title: '앨범 사진은 가족 구성원만 볼 수 있어요', description: '외부에 공유하지 않아요', tone: 'green' },
      ],
    },
    {
      label: '계정 · 보안',
      items: [
        { title: '내 PIN은 나만 알고 있어요', description: '5회 잘못 입력하면 계정이 잠겨요', tone: 'yellow' },
      ],
    },
  ],
  notice: '규칙은 관리자가 언제든 수정할 수 있어요.',
  confirmLabel: '확인했어요',
};
