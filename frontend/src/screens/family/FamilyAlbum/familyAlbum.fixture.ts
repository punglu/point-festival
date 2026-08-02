import type { FamilyAlbumModel } from './types';

export const familyAlbumFixture: FamilyAlbumModel = {
  summary: '사진 428장 · 앨범 6개',
  filters: ['전체', '여행', '기념일', '일상'],
  activeFilter: '전체',
  heroTitle: '여름 여행 · 남해',
  heroMeta: '7월 22일 · 사진 24장 · 아빠가 추가',
  recentPhotos: ['사진 1', '사진 2', '사진 3', '사진 4', '사진 5', '+7'],
  recentMeta: '7월 22일 · 12장',
  albums: [
    { title: '여름 여행', meta: '24장 · 어제', person: '아빠' },
    { title: '엄마 생일', meta: '18장 · 7월 15일', person: '서연' },
    { title: '주말 나들이', meta: '32장 · 7월 6일', person: '민준' },
  ],
};
