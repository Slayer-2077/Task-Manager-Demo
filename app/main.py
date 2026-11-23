from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from app.db import engine
from app.models import Task, User, create_tables
from app.db import get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables(engine)
    yield

    await engine.dispose()

app = FastAPI(title="My App", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="development-secret-change-me")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    completed: bool = False


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


def task_to_dict(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
    }


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI!"}

@app.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )

@app.post("/login")
async def login(request: Request, username: str=Form(...), email: str=Form(...), password: str=Form(...), Db: AsyncSession = Depends(get_session)):
    user = await Db.scalar(select(User).where(User.name == username, User.email == email, User.password == password))
    if user:
        request.session["user_id"] = user.id
        return RedirectResponse(url="/task-manager", status_code=303)
    else:
        return {"message": "Invalid credentials"}

@app.get("/register")
async def register_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
    )

@app.post("/register")
async def register(request: Request, username: str=Form(...), email: str=Form(...), password: str=Form(...), Db: AsyncSession = Depends(get_session)):
    new_user = User(name=username, email=email, password=password)
    Db.add(new_user)
    await Db.commit()
    await Db.refresh(new_user)
    request.session["user_id"] = new_user.id
    return RedirectResponse(url="/task-manager", status_code=303)


@app.get("/task-manager")
async def task_manager(request: Request):
    user_id = request.session.get("user_id")
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(request=request, name="tasks.html")


@app.get("/tasks")
async def list_tasks(request: Request, Db: AsyncSession = Depends(get_session)):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Login required")

    result = await Db.scalars(
        select(Task).where(Task.user_id == user_id).order_by(Task.id.desc())
    )
    return [task_to_dict(task) for task in result.all()]


@app.post("/tasks")
async def create_task(
    request: Request,
    task_data: TaskCreate,
    Db: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Login required")

    task = Task(user_id=user_id, **task_data.model_dump())
    Db.add(task)
    await Db.commit()
    await Db.refresh(task)
    return task_to_dict(task)


@app.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    request: Request,
    task_data: TaskUpdate,
    Db: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Login required")

    task = await Db.scalar(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await Db.commit()
    await Db.refresh(task)
    return task_to_dict(task)


@app.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    request: Request,
    Db: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Login required")

    task = await Db.scalar(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await Db.delete(task)
    await Db.commit()
    return {"message": "Task deleted successfully"}
