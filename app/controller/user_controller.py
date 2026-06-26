from uuid import UUID

from fastapi import APIRouter, status

from app.core.database import DbSession
from app.schemas.auth.response import SuccessMessage
from app.schemas.users.request import PasswordChange, RoleAssignmentRequest
from app.schemas.users.response import UserResponse
from app.services import user_services
from app.services.auth_services import AdminUser, CurrentUser

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: CurrentUser, db: DbSession):
    user = user_services.get_user_by_id(db, current_user.id)
    return user


@router.put("/change-password", response_model=SuccessMessage, status_code=status.HTTP_200_OK)
def change_password(password_change: PasswordChange, db: DbSession, current_user: CurrentUser):
    user_services.change_password(db, current_user.id, password_change)
    return SuccessMessage(message="Password changed successfully")


@router.post("/{user_id}/roles", response_model=UserResponse, status_code=status.HTTP_200_OK)
def assign_role_to_user(user_id: UUID, role_request: RoleAssignmentRequest, db: DbSession):
    user = user_services.add_role_to_user(db, user_id, role_request.role_name.lower())
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        roles=sorted(role.name for role in user.roles),
    )