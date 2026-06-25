from pydantic import BaseModel

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str


class RoleAssignmentRequest(BaseModel):
    role_name: str
