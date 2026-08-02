import type { AlbumSearchModel } from './types';

export const albumSearchFixture: AlbumSearchModel = {
  query: '여름 여행',
  summary: '사진 24장 · 앨범 1개 검색됨',
  albumTitle: '여름 여행 · 남해',
  albumMeta: '24장 · 어제',
  photos: ['여름 여행 1', '여름 여행 2', '여름 여행 3', '여름 여행 4', '여름 여행 5', '여름 여행 6'],
  recentSearches: ['엄마 생일', '민준', '주말 나들이'],
};
