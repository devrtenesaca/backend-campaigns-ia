# backend/app/infrastructure/db/callbot_campaigns.py
from __future__ import annotations

from datetime import datetime, time
from sqlalchemy import Integer, String, JSON, SmallInteger, Time, TIMESTAMP, ForeignKey,func 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.security.auth import now_utc

from app.infrastructure.db.base import Base

# Tabla Campaigns
class CampaignORM(Base):
    __tablename__ = "campaigns"
    __table_args__ = {"schema": "callbot"}

    campaign_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    campaign_type_id: Mapped[int] = mapped_column(
        ForeignKey("callbot.campaign_types.campaign_type_id", ondelete=None),  # FK normal
        nullable=False,
    )

    status: Mapped[str] = mapped_column(String(20), default="Scheduled", nullable=False)

    start_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    end_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    window_start: Mapped[time | None] = mapped_column(Time)
    window_end: Mapped[time | None] = mapped_column(Time)

    max_attempts: Mapped[int] = mapped_column(SmallInteger, default=3, nullable=False)
    retry_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    timezone: Mapped[str] = mapped_column(String(60), default="America/Guayaquil", nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    created_by: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        default=now_utc
    )

    # Relaciones
    campaign_type = relationship(
        "CampaignTypeORM",
        back_populates="campaigns", #crear relacion bidreccional para poder acceder desde CampaignTypeORM
        lazy="selectin",
    )

    contacts = relationship(
        "CampaignContactORM",
        back_populates="campaign", #crear relacion bidreccional para poder acceder desde CampaignContactORM
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    #Para debugging
    def __repr__(self) -> str: 
        return f"<CampaignORM id={self.campaign_id} name={self.name!r} status={self.status!r}>"
