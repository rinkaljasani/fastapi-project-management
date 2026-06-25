from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import InvalidPasswordError, PasswordMismatchError, UserNotFoundError
from app.models.role import Role
from app.models.user import User
from app.schemas.users.request import PasswordChange
from app.services.auth_services import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundError(user_id)
    return user


def add_role_to_user(db: Session, user_id: UUID, role_name: str) -> User:
    user = get_user_by_id(db, user_id)
    role = db.query(Role).filter(Role.name == role_name).first()

    if not role:
        role = Role(name=role_name)
        db.add(role)
        db.flush()

    if all(existing_role.name != role.name for existing_role in user.roles):
        user.roles.append(role)
        db.commit()
        db.refresh(user)

    return user


def change_password(db: Session, user_id: UUID, password_change: PasswordChange) -> None:
    user = get_user_by_id(db, user_id)

    if not verify_password(password_change.current_password, user.password_hash):
        raise InvalidPasswordError()

    if password_change.new_password != password_change.new_password_confirm:
        raise PasswordMismatchError()

    user.password_hash = get_password_hash(password_change.new_password)
    db.commit()
