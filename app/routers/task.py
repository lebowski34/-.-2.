from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Annotated
from app.backend.db_depends import get_db
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask
from slugify import slugify

router = APIRouter(prefix="/task", tags=["task"])

@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks

@router.get("/{task_id}")
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task:
        return task
    raise HTTPException(status_code=404, detail="Task was not found")

@router.post("/create")
async def create_task(task: CreateTask, user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")

    new_task = Task(**task.dict(), slug=slugify(task.title), user_id=user_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}

@router.put("/update")
async def update_task(task_id: int, task: UpdateTask, db: Annotated[Session, Depends(get_db)]):
    existing_task = db.scalar(select(Task).where(Task.id == task_id))
    if existing_task:
        for key, value in task.dict().items():
            setattr(existing_task, key, value)
        db.commit()
        db.refresh(existing_task)
        return {"status_code": status.HTTP_200_OK, "transaction": "Task update is successful!"}
    raise HTTPException(status_code=404, detail="Task was not found")

@router.delete("/delete")
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    existing_task = db.scalar(select(Task).where(Task.id == task_id))
    if existing_task:
        db.delete(existing_task)
        db.commit()
        return {"status_code": status.HTTP_200_OK, "transaction": "Task deleted successfully!"}
    raise HTTPException(status_code=404, detail="Task was not found")
