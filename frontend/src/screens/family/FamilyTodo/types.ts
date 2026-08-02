export type TodoItem = { id: string; title: string; meta: string; status: '완료' | '진행 중' | '지연' };
export type TodoGoal = { title: string; value: string; percent: number };

export type FamilyTodoModel = {
  summary: string;
  progressPercent: number;
  progressSubtitle: string;
  counts: { label: string; value: string }[];
  filters: string[];
  activeFilter: string;
  dateLabel: string;
  todos: TodoItem[];
  goals: TodoGoal[];
};

export type FamilyTodoProps = {
  model: FamilyTodoModel;
  onBack?: () => void;
  onAdd?: () => void;
  onFilter?: (filter: string) => void;
  onToggleTodo?: (todo: TodoItem) => void;
};
