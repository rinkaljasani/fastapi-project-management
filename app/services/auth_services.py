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
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.schemas.auth.request import RegisterUserRequest, TokenData
from app.schemas.auth.response import Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def register_user(db: Session, register_user_request: RegisterUserRequest) -> User:
    existing_user = db.query(User).filter(User.email == register_user_request.email).first()
    if existing_user:
        raise AuthenticationError("User already exists")

    user = User(
        email=register_user_request.email,
        first_name=register_user_request.first_name,
        last_name=register_user_request.last_name,
        password_hash=get_password_hash(register_user_request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(email: str, password: str, db: Session) -> User | bool:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(email: str, user_id: UUID, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": email, "user_id": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        user_id = payload.get("user_id")
        if not email or not user_id:
            raise AuthenticationError()
        return TokenData(user_id=user_id)
    except jwt.PyJWTError as exc:
        raise AuthenticationError() from exc


def login_for_access_token(form_data, db: Session) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise AuthenticationError("Incorrect email or password")

    access_token = create_access_token(
        user.email,
        user.id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    token_data = verify_token(token)
    user = db.query(User).filter(User.id == token_data.get_uuid()).first()
    if not user:
        raise AuthenticationError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
