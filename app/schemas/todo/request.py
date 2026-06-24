from datetime import datetime

from pydantic import BaseModel

from app.models.todo import Priority


class TodoBase(BaseModel):
    description: str
    due_date: datetime | None = None
    priority: Priority = Priority.Medium


class TodoCreate(TodoBase):
    pass