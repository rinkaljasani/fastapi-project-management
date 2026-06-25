from sqlalchemy.orm import Session
from app.schemas.comman.role_response import RoleListResponse
from app.models.role import Role

def get_roles(db: Session):
    roles = db.query(Role).all()
    return RoleListResponse(roles=roles)