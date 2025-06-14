import api.models.task as task_model
import api.schemas.task as task_schema
from sqlalchemy import select
from sqlalchemy.engine import Result

# async
from sqlalchemy.ext.asyncio import AsyncSession


# def create_task(db: Session, task_create:
#                 task_schema.TaskCreate) -> task_model.Task:
#     task = task_model.Task(**task_create.dict())
#     db.add(task)
#     db.commit()
#     db.refresh(task)
#     return task

async def create_task(
    db: AsyncSession, task_create: task_schema.TaskCreate
) -> task_model.Task:
    task = task_model.Task(**task_create.dict())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks_with_done(db: AsyncSession) -> list[tuple[int, str, bool]]:
    result: Result = await db.execute(
        select(
            task_model.Task.id,
            task_model.Task.title,
            task_model.Done.id.isnot(None).label("done"),
        ).outerjoin(task_model.Done)
    )
    return result.all()


#  U:update
async def get_task(db: AsyncSession, task_id: int) -> task_model.Task | None:
    result: Result = await db.execute(
        select(task_model.Task).filter(task_model.Task.id == task_id)
    )
    return result.scalars().first()


async def update_task(
    db: AsyncSession, task_create: task_schema.TaskCreate, original: task_model.Task
) -> task_model.Task:
    original.title = task_create.title
    db.add(original)
    await db.commit()
    await db.refresh(original)
    return original

# D:delete


async def delete_task(db: AsyncSession, original: task_model.Task) -> None:
    await db.delete(original)
    await db.commit()
