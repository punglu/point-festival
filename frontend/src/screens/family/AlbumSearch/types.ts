export type AlbumSearchModel = {
  query: string;
  summary: string;
  albumTitle: string;
  albumMeta: string;
  photos: string[];
  recentSearches: string[];
};

export type AlbumSearchProps = {
  model: AlbumSearchModel;
  onBack?: () => void;
  onCancel?: () => void;
  onClearQuery?: () => void;
  onSelectAlbum?: () => void;
  onSelectPhoto?: (photo: string) => void;
  onSelectRecent?: (query: string) => void;
};
