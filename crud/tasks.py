from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import update
from typing import Sequence
from core.models import tasks as Tasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Task
from core.schemas.tasks import TaskCreate, TaskUpdate


async def create_task(
        session: AsyncSession,
        task_create: TaskCreate,
) -> Task:
    task = Task(**task_create.dict())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task(
        session: AsyncSession,
        task_id: int
) -> Task:
    stmt = select(Task).filter(Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalars().first()
    if not task:
        raise ValueError("Task not found")
    return task


async def get_tasks(
    session: AsyncSession,
    limit: int
) -> Sequence[Task]:
    stmt = select(Task).order_by(Task.id).limit(limit)
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    return tasks


async def update_task(
        session: AsyncSession,
        task_id: int,
        task_update: TaskUpdate,
) -> Task:
    stmt = select(Task).filter(Task.id == task_id)
    result = await session.execute(stmt)
    db_task = result.scalars().first()

    if not db_task:
        raise ValueError("Task not found")

    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.description is not None:
        db_task.description = task_update.description
    if task_update.is_completed is not None:
        db_task.is_completed = task_update.is_completed

    await session.commit()
    await session.refresh(db_task)
    return db_task


async def delete_task(
        session: AsyncSession,
        task_id: int,
) -> Task:
    stmt = select(Task).filter(Task.id == task_id)
    result = await session.execute(stmt)
    db_task = result.scalars().first()

    if not db_task:
        raise ValueError("Task not found")

    await session.delete(db_task)
    await session.commit()
    return db_task

