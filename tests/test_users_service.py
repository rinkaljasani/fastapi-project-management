from uuid import uuid4

import pytest

from app.core.exceptions import InvalidPasswordError, PasswordMismatchError, UserNotFoundError
from app.models.role import Role
from app.models.user import User
from app.schemas.users.request import PasswordChange
from app.services import auth_services as auth_service
from app.services import user_services as users_service

def test_get_user_by_id(db_session, test_user):
    db_session.add(test_user)
    db_session.commit()
    
    user = users_service.get_user_by_id(db_session, test_user.id)
    assert user.id == test_user.id
    assert user.email == test_user.email
    
    with pytest.raises(UserNotFoundError):
        users_service.get_user_by_id(db_session, uuid4())

def test_change_password(db_session, test_user):
    # Add the user to the database
    db_session.add(test_user)
    db_session.commit()
    
    # Test successful password change
    password_change = PasswordChange(
        current_password="password123",  # This matches the password set in test_user fixture
        new_password="newpassword123",
        new_password_confirm="newpassword123"
    )
    
    users_service.change_password(db_session, test_user.id, password_change)
    
    # Verify new password works
    updated_user = db_session.query(User).filter_by(id=test_user.id).first()
    assert auth_service.verify_password("newpassword123", updated_user.password_hash)

def test_change_password_invalid_current(db_session, test_user):
    db_session.add(test_user)
    db_session.commit()

    # Test invalid current password
    with pytest.raises(InvalidPasswordError):
        password_change = PasswordChange(
            current_password="wrongpassword",
            new_password="newpassword123",
            new_password_confirm="newpassword123"
        )
        users_service.change_password(db_session, test_user.id, password_change)

def test_change_password_mismatch(db_session, test_user):
    db_session.add(test_user)
    db_session.commit()

    # Test password mismatch
    with pytest.raises(PasswordMismatchError):
        password_change = PasswordChange(
            current_password="password123",
            new_password="newpassword123",
            new_password_confirm="differentpassword"
        )
        users_service.change_password(db_session, test_user.id, password_change)


def test_add_role_to_user(db_session, test_user):
    db_session.add(Role(name="user"))
    db_session.add(Role(name="admin"))
    db_session.add(test_user)
    db_session.commit()

    updated_user = users_service.add_role_to_user(db_session, test_user.id, "admin")
    assert "admin" in [role.name for role in updated_user.roles]
