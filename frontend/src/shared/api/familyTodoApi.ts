/**
 * Family Todo API client (W7.5 Phase D, SLICE-TODO, canonical `1i`).
 *
 * No point/reward integration: completing a Todo never touches the
 * Markpoint Ledger. Awarding points for chores would be a real
 * business-rule decision (which todos, how much, approval or automatic)
 * this Slice does not have authority to invent — same discipline as `2c`'s
 * level-up bonus finding.
 */
import { httpClient } from './httpClient';
import type { components } from '../../generated/openapi';

type Schemas = components['schemas'];

export type FamilyTodo = Schemas['TodoOut'];

export async function listTodos(familyId: number, signal?: AbortSignal): Promise<FamilyTodo[]> {
  const { data } = await httpClient.get<FamilyTodo[]>(`/api/families/${familyId}/todos`, { signal });
  return data;
}

export async function createTodo(
  familyId: number,
  body: { title: string; assignee_membership_id?: number | null; due_at?: string | null },
): Promise<FamilyTodo> {
  const { data } = await httpClient.post<FamilyTodo>(`/api/families/${familyId}/todos`, body);
  return data;
}

export async function updateTodoStatus(familyId: number, todoId: number, status: 'open' | 'done'): Promise<FamilyTodo> {
  const { data } = await httpClient.patch<FamilyTodo>(`/api/families/${familyId}/todos/${todoId}`, { status });
  return data;
}

export async function deleteTodo(familyId: number, todoId: number): Promise<void> {
  await httpClient.delete(`/api/families/${familyId}/todos/${todoId}`);
}
