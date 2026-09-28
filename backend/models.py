from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), default="active")
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    estimated_minutes = Column(Integer, nullable=False)
    spent_minutes = Column(Integer, default=0)

    priority = Column(Integer, default=1)
    difficulty = Column(Integer, default=1)
    completed = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.now)