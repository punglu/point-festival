export type MissionCreateFormAssignee = { id: number; name: string };

export type MissionCreateFormDateMode = 'today' | 'tomorrow' | 'custom';

export type MissionCreateFormModel = {
  assignees: MissionCreateFormAssignee[];
  selectedAssigneeIds: number[];
  title: string;
  /** Folded into the submitted mission text when non-empty -- the real
   *  Mission schema has no separate description field, only free-text
   *  `text`, so this stays real rather than becoming a decorative no-op
   *  (see MissionCreateFormScreen.tsx's own onCreate handler). */
  description: string;
  point: number;
  quickPointOptions: number[];
  dateMode: MissionCreateFormDateMode;
  todayLabel: string;
  tomorrowLabel: string;
  customDate: string;
  submitting: boolean;
  canSubmit: boolean;
  validationMessage?: string | null;
};

export type MissionCreateFormSubmitPayload = {
  assigneeIds: number[];
  title: string;
  description: string;
  point: number;
  dateMode: MissionCreateFormDateMode;
  customDate: string;
};

export type MissionCreateFormProps = {
  model: MissionCreateFormModel;
  /** Product embeds this Screen inside its own modal shell (AdminModal
   *  already provides title/close/overlay) -- suppresses the frozen
   *  preview's own decorative sidebar and header close button. Detached
   *  Preview omits this prop. */
  embedded?: boolean;
  onToggleAssignee?: (id: number) => void;
  onToggleAllAssignees?: () => void;
  onTitleChange?: (value: string) => void;
  onDescriptionChange?: (value: string) => void;
  onPointChange?: (value: number) => void;
  onQuickPointSelect?: (value: number) => void;
  onDateModeChange?: (mode: MissionCreateFormDateMode) => void;
  onCustomDateChange?: (value: string) => void;
  onCancel?: () => void;
  onCreate?: (payload: MissionCreateFormSubmitPayload) => void;
};
