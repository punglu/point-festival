export type AlbumSummary = { title: string; meta: string; person: string };

export type FamilyAlbumModel = {
  summary: string;
  filters: string[];
  activeFilter: string;
  heroTitle: string;
  heroMeta: string;
  recentPhotos: string[];
  recentMeta: string;
  albums: AlbumSummary[];
};

export type FamilyAlbumProps = {
  model: FamilyAlbumModel;
  onBack?: () => void;
  onSearch?: () => void;
  onUpload?: () => void;
  onFilter?: (filter: string) => void;
  onSelectPhoto?: (photo: string) => void;
  onSelectAlbum?: (album: AlbumSummary) => void;
};
