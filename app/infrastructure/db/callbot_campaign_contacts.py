# backend/app/infraestructure/db/callbot_campaign_contacts.py
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Integer, String, Text, JSON, SmallInteger, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base
from app.security.auth import now_utc

class CampaignContactORM(Base):
    __tablename__ = "campaign_contacts"
    __table_args__ = {"schema": "callbot"}

    campaign_contact_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("callbot.campaigns.campaign_id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Datos de contacto
    phone: Mapped[str] = mapped_column(String(25), nullable=False)
    name: Mapped[str | None] = mapped_column(String(120))
    attributes: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Estado
    status: Mapped[str] = mapped_column(String(20), default="Pending", nullable=False)
    attempt_count: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    next_attempt_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    last_disposition: Mapped[str | None] = mapped_column(String(60))
    last_error: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    source_batch_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),  default=now_utc)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    created_by: Mapped[str] = mapped_column(String(80), nullable=False)

    # Relación con CampaignORM
    campaign = relationship(
        "CampaignORM", 
        back_populates="contacts", 
        lazy="selectin")


