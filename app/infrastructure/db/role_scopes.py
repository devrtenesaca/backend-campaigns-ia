from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class RoleScopeORM(Base):
    __tablename__ = "role_scopes"
    __table_args__ = {"schema": "auth"}

    role_id: Mapped[int] = mapped_column(ForeignKey("auth.roles.id", ondelete="CASCADE"), primary_key=True)
    scope_id: Mapped[int] = mapped_column(ForeignKey("auth.scopes.id", ondelete="CASCADE"), primary_key=True)
