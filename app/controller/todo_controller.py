from typing import List
from uuid import UUID

from fastapi import APIRouter, status

from app.core.database import DbSession
from app.schemas.todo.request import TodoCreate
from app.schemas.todo.response import TodoResponse
from app.services import todo_services
from app.services.auth_services import CurrentUser

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(db: DbSession, todo: TodoCreate, current_user: CurrentUser):
    return todo_services.create_todo(current_user, db, todo)


@router.get("/", response_model=List[TodoResponse])
def get_todos(db: DbSession, current_user: CurrentUser):
    return todo_services.get_todos(current_user, db)


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(db: DbSession, todo_id: UUID, current_user: CurrentUser):
    return todo_services.get_todo_by_id(current_user, db, todo_id)


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(db: DbSession, todo_id: UUID, todo_update: TodoCreate, current_user: CurrentUser):
    return todo_services.update_todo(current_user, db, todo_id, todo_update)


@router.put("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(db: DbSession, todo_id: UUID, current_user: CurrentUser):
    return todo_services.complete_todo(current_user, db, todo_id)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(db: DbSession, todo_id: UUID, current_user: CurrentUser):
    todo_services.delete_todo(current_user, db, todo_id)