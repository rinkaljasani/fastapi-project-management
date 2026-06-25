
from fastapi import APIRouter
from starlette import status

from app.schemas.comman.role_response import RoleListResponse
from app.core.database import DbSession
from app.services import comman_services


router = APIRouter()

@router.get(
    "/roles",
    response_model=RoleListResponse,
    status_code=status.HTTP_200_OK,
)
def get_roles(db: DbSession):
    return comman_services.get_roles(db)