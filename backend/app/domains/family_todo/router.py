from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.family.dependencies import get_family_membership
from app.domains.family.models import FamilyMembership
from . import service
from .schemas import TodoCreate, TodoOut, TodoUpdate

router = APIRouter(tags=["family-todo"])


@router.get("/api/families/{family_id}/todos", response_model=list[TodoOut])
async def list_todos(family_id: int, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.list_todos(db, family_id)


@router.post("/api/families/{family_id}/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
async def create_todo(family_id: int, body: TodoCreate, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.create_todo(db, family_id, actor, title=body.title, assignee_membership_id=body.assignee_membership_id, due_at=body.due_at)


@router.patch("/api/families/{family_id}/todos/{todo_id}", response_model=TodoOut)
async def update_todo(family_id: int, todo_id: int, body: TodoUpdate, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.update_todo(db, family_id, todo_id, title=body.title, assignee_membership_id=body.assignee_membership_id, due_at=body.due_at, status_value=body.status)


@router.delete("/api/families/{family_id}/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(family_id: int, todo_id: int, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    await service.delete_todo(db, family_id, todo_id)
