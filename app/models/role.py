import uuid

from sqlalchemy import Column, ForeignKey, String, Table, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from app.core.database import Base
from app.models.user import User

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Uuid(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("role_id", Uuid(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
    
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(250), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True),nullable=False,default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True),nullable=False,default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))
    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role(name='{self.name}')>"
