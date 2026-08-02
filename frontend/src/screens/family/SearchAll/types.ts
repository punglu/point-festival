export type SearchResultItem = { icon: string; iconTone: 'blue' | 'green' | 'purple'; titleParts: (string | { hl: string })[]; meta: string };
export type SearchResultGroup = { label: string; items: SearchResultItem[] };
export type SearchAllModel = {
  query: string;
  cancelLabel: string;
  filters: string[];
  activeFilter: string;
  groups: SearchResultGroup[];
  recentSearches: string[];
};
export type SearchAllProps = { model: SearchAllModel; onBack?: () => void; onCancel?: () => void; onFilter?: (f: string) => void };
