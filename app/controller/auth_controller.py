from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.core.database import DbSession
from app.schemas.auth.request import RegisterUserRequest
from app.schemas.auth.response import SuccessMessage, Token
from app.services import auth_services
from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from datetime import datetime, timezone

from datetime import datetime, timezone

from fastapi import HTTPException

from app.models.user import User
from app.core.mail import decode_verification_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=SuccessMessage, status_code=status.HTTP_201_CREATED)
async def register_user(db: DbSession, register_user_request: RegisterUserRequest):
    await auth_services.register_user(db, register_user_request)
    return SuccessMessage(message="User registered successfully")


@router.post("/login", response_model=Token)
def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: DbSession):
    return auth_services.login_for_access_token(form_data, db)


@router.get("/verify-email")
def verify_email(
    token: str,
    db: DbSession
):

    email = decode_verification_token(token)
    user = (db.query(User).filter(User.email == email).first())

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.is_verified:
        return {
            "message": "Email already verified"
        }

    user.is_verified = True
    user.verified_at = datetime.now(
        timezone.utc
    )

    db.commit()

    return {
        "message": "Email verified successfully"
    }