from fastapi import APIRouter, status

from app.core.database import DbSession
from app.schemas.auth.response import SuccessMessage
from app.schemas.users.request import PasswordChange
from app.schemas.users.response import UserResponse
from app.services import user_services
from app.services.auth_services import CurrentUser

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: CurrentUser, db: DbSession):
    return user_services.get_user_by_id(db, current_user.id)


@router.put("/change-password", response_model=SuccessMessage, status_code=status.HTTP_200_OK)
def change_password(password_change: PasswordChange, db: DbSession, current_user: CurrentUser):
    user_services.change_password(db, current_user.id, password_change)
    return SuccessMessage(message="Password changed successfully")

