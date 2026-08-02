import type { AccountDeletionConfirmModel } from './types';
export const accountDeletionConfirmFixture: AccountDeletionConfirmModel = {
  title: '계정 탈퇴',
  question: '정말 탈퇴하시겠어요?',
  itemsIntro: '탈퇴 시 아래 내용이 모두 삭제돼요',
  items: ['보유 포인트 320P', '완료한 미션 기록 48건', '앨범 사진 및 대화 기록'],
  confirmHint: '계속하려면 "탈퇴합니다"를 입력하세요',
  confirmWord: '탈퇴합니다',
};
