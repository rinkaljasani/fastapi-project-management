from uuid import uuid4

import pytest

from app.core.exceptions import TodoNotFoundError
from app.models.todo import Todo
from app.schemas.todo.request import TodoCreate
from app.services import todo_services

class TestTodosService:
    def test_create_todo(self, db_session, test_user):
        todo_create = TodoCreate(
            description="New Description"
        )
        db_session.add(test_user)
        db_session.commit()

        new_todo = todo_services.create_todo(test_user, db_session, todo_create)
        assert new_todo.description == "New Description"
        assert new_todo.user_id == test_user.id
        assert not new_todo.is_completed

    def test_get_todos(self, db_session, test_user, test_todo):
        db_session.add(test_user)
        test_todo.user_id = test_user.id
        db_session.add(test_todo)
        db_session.commit()
        
        todos = todo_services.get_todos(test_user, db_session)
        assert len(todos) == 1
        assert todos[0].id == test_todo.id

    def test_get_todo_by_id(self, db_session, test_user, test_todo):
        db_session.add(test_user)
        test_todo.user_id = test_user.id
        db_session.add(test_todo)
        db_session.commit()
        
        todo = todo_services.get_todo_by_id(test_user, db_session, test_todo.id)
        assert todo.id == test_todo.id
        
        with pytest.raises(TodoNotFoundError):
            todo_services.get_todo_by_id(test_user, db_session, uuid4())

    def test_complete_todo(self, db_session, test_user, test_todo):
        db_session.add(test_user)
        test_todo.user_id = test_user.id
        db_session.add(test_todo)
        db_session.commit()
        
        completed_todo = todo_services.complete_todo(test_user, db_session, test_todo.id)
        assert completed_todo.is_completed
        assert completed_todo.completed_at is not None

    def test_delete_todo(self, db_session, test_user, test_todo):
        db_session.add(test_user)
        test_todo.user_id = test_user.id
        db_session.add(test_todo)
        db_session.commit()
        
        todo_services.delete_todo(test_user, db_session, test_todo.id)
        assert db_session.query(Todo).filter_by(id=test_todo.id).first() is None 
