from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class RevokedAccessTokenORM(Base):
    __tablename__ = "revoked_access_tokens"
    __table_args__ = {"schema": "auth"}

    jti: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)  # string UUID del claim jti
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
