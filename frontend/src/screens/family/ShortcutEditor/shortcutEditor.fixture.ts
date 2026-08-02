import type { ShortcutEditorModel } from './types';
export const shortcutEditorFixture: ShortcutEditorModel = {
  title: '바로가기 편집',
  subtitle: '홈 화면 상단에 표시할 바로가기 4개를 골라주세요 (2/4 선택됨)',
  selectedLabel: '선택됨',
  addMoreLabel: '더 추가하기',
  items: [
    { icon: '⚑', label: '포인트 잔치', selected: true },
    { icon: '▦', label: '가족 일정', selected: true },
    { icon: '▢', label: '앨범', selected: false },
    { icon: '◔', label: '대화', selected: false },
    { icon: '≡', label: '할 일', selected: false },
    { icon: '≡', label: '게시판', selected: false },
  ],
  confirmLabel: '완료',
};
