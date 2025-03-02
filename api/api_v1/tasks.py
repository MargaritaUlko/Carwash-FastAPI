from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from core.models import db_helper
from core.schemas.tasks import (
    TaskCreate,
    TaskUpdate,
    TaskInDB,
)
from crud import tasks as tasks_crud

router = APIRouter(
    prefix=settings.api.v1.tasks,
    tags=["Tasks"],
)

@router.get("", response_model=list[TaskInDB])
async def get_tasks(
    session: AsyncSession = Depends(db_helper.session_getter),
    limit: int = 10,
):
    tasks = await tasks_crud.get_tasks(session=session, limit=limit)
    return tasks


@router.get("/{task_id}", response_model=TaskInDB)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await tasks_crud.get_task(session=session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=TaskInDB, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await tasks_crud.create_task(session=session, task_create=task_create)
    return task



@router.put("/{task_id}", response_model=TaskInDB)
async def update_task(
    task_update: TaskUpdate,
    task_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),

):
    task = await tasks_crud.update_task(
        session=session, task_id=task_id, task_update=task_update
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    deleted = await tasks_crud.delete_task(session=session, task_id=task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}


@router.patch("/{task_id}/complete", response_model=TaskInDB)
async def complete_task(
        task_id: int,
        session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await tasks_crud.get_task(session=session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_completed = True
    await session.commit()
    await session.refresh(task)
    return task