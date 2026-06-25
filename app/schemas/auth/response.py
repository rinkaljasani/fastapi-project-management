from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str
    roles: list[str] = Field(default_factory=list)


class SuccessMessage(BaseModel):
    message: str
