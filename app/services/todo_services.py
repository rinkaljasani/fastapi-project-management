from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import TodoCreationError, TodoNotFoundError
from app.models.todo import Todo
from app.models.user import User
from app.schemas.todo.request import TodoCreate


def create_todo(current_user: User, db: Session, todo: TodoCreate) -> Todo:
    try:
        new_todo = Todo(**todo.model_dump(), user_id=current_user.id)
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return new_todo
    except Exception as exc:
        db.rollback()
        raise TodoCreationError(str(exc)) from exc


def get_todos(current_user: User, db: Session) -> list[Todo]:
    return db.query(Todo).filter(Todo.user_id == current_user.id).all()


def get_todo_by_id(current_user: User, db: Session, todo_id: UUID) -> Todo:
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
    if not todo:
        raise TodoNotFoundError(todo_id)
    return todo


def update_todo(current_user: User, db: Session, todo_id: UUID, todo_update: TodoCreate) -> Todo:
    todo = get_todo_by_id(current_user, db, todo_id)
    for field, value in todo_update.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo


def complete_todo(current_user: User, db: Session, todo_id: UUID) -> Todo:
    todo = get_todo_by_id(current_user, db, todo_id)
    if not todo.is_completed:
        todo.is_completed = True
        todo.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(todo)
    return todo


def delete_todo(current_user: User, db: Session, todo_id: UUID) -> None:
    todo = get_todo_by_id(current_user, db, todo_id)
    db.delete(todo)
    db.commit()