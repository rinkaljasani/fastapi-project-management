from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import InvalidPasswordError, PasswordMismatchError, UserNotFoundError
from app.models.user import User
from app.schemas.users.request import PasswordChange
from app.services.auth_services import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundError(user_id)
    return user


def change_password(db: Session, user_id: UUID, password_change: PasswordChange) -> None:
    user = get_user_by_id(db, user_id)

    if not verify_password(password_change.current_password, user.password_hash):
        raise InvalidPasswordError()

    if password_change.new_password != password_change.new_password_confirm:
        raise PasswordMismatchError()

    user.password_hash = get_password_hash(password_change.new_password)
    db.commit()