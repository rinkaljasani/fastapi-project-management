from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import DbSession
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.role import Role
from app.models.user import User
from app.schemas.auth.request import RegisterUserRequest, TokenData
from app.schemas.auth.response import Token
from fastapi import HTTPException

from app.services.email_services import send_verification_email
from app.core.mail import create_verification_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
DEFAULT_ROLE_NAME = "user"
ADMIN_ROLE_NAME = "admin"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def ensure_role(db: Session, role_name: str) -> Role:
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name)
        db.add(role)
        db.flush()
    return role


def ensure_default_roles(db: Session) -> None:
    ensure_role(db, DEFAULT_ROLE_NAME)
    ensure_role(db, ADMIN_ROLE_NAME)
    db.commit()


def get_user_role_names(user: User) -> list[str]:
    return sorted(role.name for role in user.roles)


async def register_user(db: Session, register_user_request: RegisterUserRequest) -> User:
    ensure_default_roles(db)
    existing_user = db.query(User).filter(User.email == register_user_request.email).first()
    if existing_user:
        raise AuthenticationError("User already exists")

    default_role = ensure_role(db, DEFAULT_ROLE_NAME)
    user = User(
        email=register_user_request.email,
        first_name=register_user_request.first_name,
        last_name=register_user_request.last_name,
        password_hash=get_password_hash(register_user_request.password),
        roles=[default_role],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_verification_token(user.email)

    verification_link = (
        f"http://localhost:8000/auth/verify-email?token={token}"
    )

    await send_verification_email(
        user.email,
        verification_link
    )

    return user


def authenticate_user(email: str, password: str, db: Session) -> User | bool:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(email: str, user_id: UUID, roles: list[str], expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": email, "user_id": str(user_id), "roles": roles, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        user_id = payload.get("user_id")
        roles = payload.get("roles", [])
        if not email or not user_id:
            raise AuthenticationError()
        return TokenData(user_id=user_id, roles=roles)
    except jwt.PyJWTError as exc:
        raise AuthenticationError() from exc


def login_for_access_token(form_data, db: Session) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise AuthenticationError("Incorrect email or password")
    
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email first"
        )
    access_token = create_access_token(
        user.email,
        user.id,
        get_user_role_names(user),
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer", roles=get_user_role_names(user))


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    token_data = verify_token(token)
    user = db.query(User).filter(User.id == token_data.get_uuid()).first()
    if not user:
        raise AuthenticationError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*required_roles: str):
    def dependency(current_user: CurrentUser) -> User:
        user_roles = set(get_user_role_names(current_user))
        if not any(role in user_roles for role in required_roles):
            raise AuthorizationError()
        return current_user

    return dependency


AdminUser = Annotated[User, Depends(require_roles(ADMIN_ROLE_NAME))]
