from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.todo import Priority


class TodoResponse(BaseModel):
    id: UUID
    description: str
    due_date: datetime | None = None
    priority: Priority
    is_completed: bool
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
