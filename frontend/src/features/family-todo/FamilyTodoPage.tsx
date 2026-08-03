import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyTodoScreen, familyTodoFixture } from '../../screens/family/FamilyTodo';
import type { TodoItem } from '../../screens/family/FamilyTodo';
import { listTodos, updateTodoStatus, type FamilyTodo } from '../../shared/api/familyTodoApi';
import { listFamilyMembers, type FamilyMembershipSummary } from '../../shared/api/familyApi';
import { useFamilyContextStore } from '../../shared/stores/useFamilyContextStore';
import styles from './FamilyTodoPage.module.css';

function dateLabel(d: Date): string {
  const days = ['일', '월', '화', '수', '목', '금', '토'];
  return `${d.getMonth() + 1}월 ${d.getDate()}일 (${days[d.getDay()]})`;
}

function toTodoItem(todo: FamilyTodo, nameByMembershipId: Map<number, string>): TodoItem {
  const assigneeName = todo.assignee_membership_id !== null ? nameByMembershipId.get(todo.assignee_membership_id) : undefined;
  const isLate = todo.status === 'open' && todo.due_at !== null && new Date(todo.due_at).getTime() < Date.now();
  const status: TodoItem['status'] = todo.status === 'done' ? '완료' : isLate ? '지연' : '진행 중';
  const dueText = todo.due_at
    ? isLate
      ? `${new Date(todo.due_at).toLocaleDateString('ko-KR')} 마감`
      : `${new Date(todo.due_at).toLocaleDateString('ko-KR')}까지`
    : undefined;
  const meta = [assigneeName, dueText].filter(Boolean).join(' · ') || '담당자 없음';
  return { id: String(todo.id), title: todo.title, meta, status };
}

/**
 * `/family/todo` — canonical 1i (할 일, W7.5 Phase D SLICE-TODO).
 *
 * List and toggle-complete are real (`GET/PATCH /api/families/{id}/todos`).
 * **Creating a new Todo stays a disclosed gap, not a backend gap**: the
 * frozen canonical Screen's "＋ 할 일 추가" button has no form/input behind
 * it to collect a title from — `onAdd` is intentionally not wired to a
 * fabricated create call. `goals` (이번 주 가족 목표) has no backing data
 * model at all and is rendered empty rather than showing the fixture's
 * invented numbers.
 */
export function FamilyTodoPage() {
  const navigate = useNavigate();
  const activeFamilyId = useFamilyContextStore((s) => s.activeFamilyId);
  const [filter, setFilter] = useState(familyTodoFixture.activeFilter);
  const [todos, setTodos] = useState<FamilyTodo[] | null>(null);
  const [members, setMembers] = useState<FamilyMembershipSummary[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (activeFamilyId === null) return undefined;
    const controller = new AbortController();
    setLoadError(null);
    Promise.all([listTodos(activeFamilyId, controller.signal), listFamilyMembers(activeFamilyId, controller.signal)])
      .then(([todoList, memberList]) => {
        setTodos(todoList);
        setMembers(memberList);
      })
      .catch(() => { if (!controller.signal.aborted) setLoadError('할 일을 불러오지 못했어요.'); });
    return () => controller.abort();
  }, [activeFamilyId]);

  const nameByMembershipId = useMemo(() => new Map(members.map((m) => [m.id, m.account_display_name])), [members]);

  const toggle = async (item: TodoItem) => {
    if (activeFamilyId === null || todos === null) return;
    const nextStatus = item.status === '완료' ? 'open' : 'done';
    setLoadError(null);
    try {
      const updated = await updateTodoStatus(activeFamilyId, Number(item.id), nextStatus);
      setTodos((prev) => (prev ?? []).map((t) => (t.id === updated.id ? updated : t)));
    } catch {
      setLoadError('할 일 상태를 변경하지 못했어요.');
    }
  };

  const realTodos = (todos ?? []).map((t) => toTodoItem(t, nameByMembershipId));
  const memberFilters = members.map((m) => m.account_display_name);
  const filters = ['우리 가족', ...memberFilters, '완료'];
  const visibleTodos = realTodos.filter((t) => {
    if (filter === '우리 가족') return true;
    if (filter === '완료') return t.status === '완료';
    return t.meta.startsWith(filter);
  });
  const doneCount = realTodos.filter((t) => t.status === '완료').length;
  const inProgressCount = realTodos.filter((t) => t.status === '진행 중').length;
  const lateCount = realTodos.filter((t) => t.status === '지연').length;
  const total = realTodos.length;

  // Load failure must never fall back to fixture todos -- a real empty/
  // error list, not five invented items, per the Test Policy's own
  // API-failure-must-not-mask-as-fixture-success rule.
  const isLoadFailure = loadError !== null && todos === null;

  const model = {
    summary: isLoadFailure ? loadError : `오늘 ${total}개 · 완료 ${doneCount}개`,
    progressPercent: isLoadFailure ? 0 : total > 0 ? Math.round((doneCount / total) * 100) : 0,
    progressSubtitle: isLoadFailure ? '' : `${total - doneCount}개 남았어요${lateCount > 0 ? ` · 지연 ${lateCount}개` : ''}`,
    counts: [
      { label: '완료', value: `${doneCount}개` },
      { label: '진행 중', value: `${inProgressCount}개` },
      { label: '지연', value: `${lateCount}개` },
    ],
    filters,
    activeFilter: filters.includes(filter) ? filter : '우리 가족',
    dateLabel: dateLabel(new Date()),
    todos: isLoadFailure ? [] : visibleTodos,
    goals: [],
  };

  return (
    <div className={styles.wrap}>
      <FamilyTodoScreen
        model={model}
        onBack={() => navigate('/family')}
        onFilter={setFilter}
        onToggleTodo={(todo) => void toggle(todo)}
      />
      {/* Load failures already surface inline via `summary` above (todos
          stays null). A toggle failure happens after todos is already
          populated, so it needs its own visible banner -- otherwise a
          failed status change would look identical to a successful one. */}
      {todos !== null && loadError && <p className={styles.error} role="alert">{loadError}</p>}
    </div>
  );
}
