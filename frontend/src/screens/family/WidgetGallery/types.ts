export type WidgetGalleryModel = {
  title: string;
  subtitle: string;
  sizes: string[];
  activeSize: string;
  point: { label: string; name: string; value: string; delta: string };
  mission: { label: string; title: string; progress: string; items: { text: string; done: boolean }[] };
  schedule: { label: string; title: string; items: { color: string; text: string; date: string }[] };
  confirmLabel: string;
};
export type WidgetGalleryProps = { model: WidgetGalleryModel; onBack?: () => void; onConfirm?: () => void; onSelectSize?: (size: string) => void };
