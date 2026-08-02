import type { WidgetGalleryModel } from './types';
export const widgetGalleryFixture: WidgetGalleryModel = {
  title: '위젯',
  subtitle: '홈 화면에 추가해서 바로 확인해요',
  sizes: ['작게', '중간', '크게'],
  activeSize: '작게',
  point: { label: '포인트 위젯 · 작게', name: '서연', value: '320P', delta: '오늘 +40P' },
  mission: {
    label: '오늘의 미션 위젯 · 중간',
    title: '오늘의 미션',
    progress: '2/3 완료',
    items: [
      { text: '방 청소하기', done: true },
      { text: '재활용 분리배출', done: true },
      { text: '숙제 다 하기', done: false },
    ],
  },
  schedule: {
    label: '가족 일정 위젯 · 큰',
    title: '다가오는 일정',
    items: [
      { color: 'purple', text: '가족 저녁 · 삼겹살', date: '오늘' },
      { color: 'yellow', text: '엄마 생일', date: '7/25' },
      { color: 'green', text: '여름 여행 출발', date: '7/29' },
    ],
  },
  confirmLabel: '위젯 추가하기',
};
