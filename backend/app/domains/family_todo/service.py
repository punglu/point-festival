"""Family Todo application service. Any active Family member may manage the
shared list -- this is a collaborative chore list, not an admin-gated
Markpoint Mission, so no extra permission code is required beyond active
Membership (already enforced by `get_family_membership` at the router)."""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.family.models import FamilyMembership
from .models import FamilyTodo


def _now():
    return datetime.now(timezone.utc)


async def _validate_assignee(db: AsyncSession, family_id: int, membership_id: int | None) -> None:
    if membership_id is None:
        return
    row = await db.get(FamilyMembership, membership_id)
    if row is None or row.family_group_id != family_id or row.status != "active" or row.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="활성 가족 구성원만 담당자로 지정할 수 있습니다")


async def list_todos(db: AsyncSession, family_id: int) -> list[FamilyTodo]:
    stmt = select(FamilyTodo).where(FamilyTodo.family_group_id == family_id).order_by(FamilyTodo.status, FamilyTodo.due_at.is_(None), FamilyTodo.due_at, FamilyTodo.id)
    return list((await db.execute(stmt)).scalars())


async def create_todo(db: AsyncSession, family_id: int, actor: FamilyMembership, *, title: str, assignee_membership_id: int | None, due_at) -> FamilyTodo:
    await _validate_assignee(db, family_id, assignee_membership_id)
    todo = FamilyTodo(family_group_id=family_id, assignee_membership_id=assignee_membership_id, created_by_membership_id=actor.id, title=title, due_at=due_at, status="open")
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo


async def _get(db: AsyncSession, family_id: int, todo_id: int) -> FamilyTodo:
    todo = await db.get(FamilyTodo, todo_id)
    if todo is None or todo.family_group_id != family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="할 일을 찾을 수 없습니다")
    return todo


async def update_todo(db: AsyncSession, family_id: int, todo_id: int, *, title: str | None, assignee_membership_id: int | None, due_at, status_value: str | None) -> FamilyTodo:
    todo = await _get(db, family_id, todo_id)
    if assignee_membership_id is not None:
        await _validate_assignee(db, family_id, assignee_membership_id)
        todo.assignee_membership_id = assignee_membership_id
    if title is not None:
        todo.title = title
    if due_at is not None:
        todo.due_at = due_at
    if status_value is not None and status_value != todo.status:
        todo.status = status_value
        todo.completed_at = _now() if status_value == "done" else None
    await db.commit()
    await db.refresh(todo)
    return todo


async def delete_todo(db: AsyncSession, family_id: int, todo_id: int) -> None:
    todo = await _get(db, family_id, todo_id)
    await db.delete(todo)
    await db.commit()
