from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class UserRoleORM(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "auth"}

    user_id: Mapped[int] = mapped_column(ForeignKey("auth.users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("auth.roles.id", ondelete="CASCADE"), primary_key=True)
