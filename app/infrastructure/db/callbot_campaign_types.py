from __future__ import annotations
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base
from app.infrastructure.db.callbot_campaigns import CampaignORM

#Tabla Campaign Types
class CampaignTypeORM(Base):
    __tablename__ = "campaign_types"
    __table_args__ = {"schema": "callbot"}

    campaign_type_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    # Relación con CampaignORM
    campaigns: Mapped[list["CampaignORM"]] = relationship(
        "CampaignORM",
        back_populates="campaign_type",
        lazy="selectin",
        cascade="all, delete",
        passive_deletes=True,
    )

