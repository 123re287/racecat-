from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    deadline: datetime


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    deadline: datetime
    created_at: datetime
    status: str

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    project_id: int
    title: str
    description: str | None = None
    estimated_minutes: int
   
    priority: int = 1
    difficulty: int = 1


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    estimated_minutes: int
    spent_minutes: int
    priority: int
    difficulty: int
    completed: int
    created_at: datetime

class TaskProgressUpdate(BaseModel):
    minutes: int

    class Config:
        from_attributes = True
    class Config:
        from_attributes = True