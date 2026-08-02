import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { FamilyTodoScreen, familyTodoFixture } from '../../screens/family/FamilyTodo';
import type { TodoItem } from '../../screens/family/FamilyTodo';
import styles from './FamilyTodoPage.module.css';

/**
 * `/family/todo` — canonical 1i (할 일, CHILD_OF 1b, ROOT within this
 * feature — no further children declared in the W7.1 Ownership Matrix).
 * frontend/src/features/family-todo/ was an empty scaffold. No real todo
 * API is wired (TRUE_FUNCTIONAL_GAP for mutation) — real local toggle state
 * is used to keep the interaction genuine within Screen-local UI state,
 * per the W7.4 boundary.
 */
export function FamilyTodoPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState(familyTodoFixture.activeFilter);
  const [todos, setTodos] = useState(familyTodoFixture.todos);

  const toggle = (todo: TodoItem) => {
    setTodos((prev) => prev.map((t) => (t.id === todo.id ? { ...t, status: t.status === '완료' ? '진행 중' : '완료' } : t)));
  };

  return (
    <div className={styles.wrap}>
      <FamilyTodoScreen
        model={{ ...familyTodoFixture, todos, activeFilter: filter }}
        onBack={() => navigate('/family')}
        onFilter={setFilter}
        onToggleTodo={toggle}
      />
    </div>
  );
}
