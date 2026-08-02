export type FileViewerItem = { label: string; isFile?: boolean };

export type FileViewerModel = {
  title: string;
  subtitle: string;
  tabs: string[];
  activeTab: string;
  recentFiles: FileViewerItem[];
  todaySectionLabel: string;
  todayFiles: FileViewerItem[];
};

export type FileViewerProps = {
  model: FileViewerModel;
  onBack?: () => void;
  onSelectMode?: () => void;
  onTab?: (tab: string) => void;
  onSelectFile?: (file: FileViewerItem) => void;
};
