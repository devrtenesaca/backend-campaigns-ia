from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class RoleORM(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    users: Mapped[list["UserORM"]] = relationship(
        secondary="auth.user_roles",
        back_populates="roles",
        lazy="selectin",
    )
    scopes: Mapped[list["ScopeORM"]] = relationship(
        secondary="auth.role_scopes",
        back_populates="roles",
        lazy="selectin",
    )
