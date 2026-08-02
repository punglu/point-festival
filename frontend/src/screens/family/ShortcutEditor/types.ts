export type ShortcutItem = { icon: string; label: string; selected: boolean };
export type ShortcutEditorModel = {
  title: string;
  subtitle: string;
  selectedLabel: string;
  addMoreLabel: string;
  items: ShortcutItem[];
  confirmLabel: string;
};
export type ShortcutEditorProps = { model: ShortcutEditorModel; onBack?: () => void; onConfirm?: () => void; onToggle?: (label: string) => void };
