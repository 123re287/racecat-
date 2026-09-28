from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Project, Task
from schemas import (
    ProjectCreate,
    ProjectResponse,
    TaskCreate,
    TaskResponse,
    TaskProgressUpdate
)

from services.recommender import (
    calculate_task_score,
    calculate_daily_workload,
    allocate_daily_minutes
    )

from fastapi.staticfiles import StaticFiles
app = FastAPI(title="赛程猫")

app.mount(
    "/frontend",
    StaticFiles(directory="../frontend", html=True),
    name="frontend"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




@app.post("/projects", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    new_project = Project(
        name=project.name,
        description=project.description,
        deadline=project.deadline
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@app.get("/projects", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@app.get("/projects/{project_id}/countdown")
def get_countdown(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        return {"error": "赛程不存在"}

    now = datetime.now()
    remaining = project.deadline - now

    return {
        "project": project.name,
        "deadline": project.deadline,
        "days": remaining.days,
        "hours": remaining.seconds // 3600,
        "minutes": (remaining.seconds % 3600) // 60
    }


@app.post("/tasks", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    new_task = Task(
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        estimated_minutes=task.estimated_minutes,
        priority=task.priority,
        difficulty=task.difficulty
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
def get_tasks(
    project_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Task).filter(
        Task.project_id == project_id
    ).all()

@app.get("/projects/{project_id}/recommend")
def recommend_tasks(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        return {"error": "赛程不存在"}

    tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.completed == 0
    ).all()

    total_remaining_minutes = sum(
        max(task.estimated_minutes - task.spent_minutes, 0)
        for task in tasks
    )

    now = datetime.now()
    days_left = (project.deadline - now).days

    daily_target_minutes = calculate_daily_workload(
        total_remaining_minutes,
        days_left
    )

    result = []

    for task in tasks:
        score = calculate_task_score(
            task.priority,
            task.difficulty,
            task.estimated_minutes,
            days_left
        )

        result.append({
            "task_id": task.id,
            "title": task.title,
            "score": score,
            "remaining_minutes": max(
                task.estimated_minutes - task.spent_minutes,
                0
            )
        })

    result.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    today_tasks = allocate_daily_minutes(
        result,
        daily_target_minutes
    )
    completed_minutes = sum(
        task.spent_minutes
        for task in tasks
    )
    return {
        "daily_target_minutes": daily_target_minutes,
        "completed_minutes": completed_minutes,
        "today_tasks": today_tasks,
        "all_tasks": result
    }
@app.put("/tasks/{task_id}/progress")
def update_task_progress(
    task_id: int,
    progress: TaskProgressUpdate,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        return {"error": "任务不存在"}

    task.spent_minutes += progress.minutes

    db.commit()
    db.refresh(task)

    return {
        "message": "任务进度已更新",
        "task_id": task.id,
        "title": task.title,
        "spent_minutes": task.spent_minutes
    }

@app.put("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        return {"error": "任务不存在"}

    if task.spent_minutes < task.estimated_minutes:
        return {
            "error": "任务还没有完成",
            "spent_minutes": task.spent_minutes,
            "estimated_minutes": task.estimated_minutes
        }

    task.completed = 1

    db.commit()
    db.refresh(task)

    return {
        "message": "任务完成！",
        "task_id": task.id,
        "title": task.title,
        "completed": task.completed
    }
