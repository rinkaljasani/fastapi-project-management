from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.core.database import DbSession
from app.schemas.auth.request import RegisterUserRequest
from app.schemas.auth.response import SuccessMessage, Token
from app.services import auth_services

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=SuccessMessage, status_code=status.HTTP_201_CREATED)
def register_user(db: DbSession, register_user_request: RegisterUserRequest):
    auth_services.register_user(db, register_user_request)
    return SuccessMessage(message="User registered successfully")


@router.post("/login", response_model=Token)
def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: DbSession):
    return auth_services.login_for_access_token(form_data, db)