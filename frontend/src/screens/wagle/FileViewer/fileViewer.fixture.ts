import type { FileViewerModel } from './types';

const files = ['여름 여행 1', '여름 여행 2', '여름 여행 3', '가족 일정.pdf', '독서록.jpg', '추억 영상'];

export const fileViewerFixture: FileViewerModel = {
  title: '사진/파일',
  subtitle: '우리 가족방',
  tabs: ['전체', '사진', '파일'],
  activeTab: '전체',
  recentFiles: files.map((label, index) => ({ label, isFile: index > 2 })),
  todaySectionLabel: '7월 22일',
  todayFiles: files.slice(0, 3).map((label) => ({ label })),
};
