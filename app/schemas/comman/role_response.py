from uuid import UUID
from pydantic import BaseModel, ConfigDict


class RoleItem(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)
class RoleListResponse(BaseModel):
    roles: list[RoleItem]