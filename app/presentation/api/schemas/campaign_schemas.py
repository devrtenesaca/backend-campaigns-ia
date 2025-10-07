# backend/app/presentation/api/schemas/campaign_schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime, time

class CampaignCreateIn(BaseModel):
    name: str
    campaign_type_id: int
    start_at: datetime
    end_at: Optional[datetime] = None
    window_start: Optional[time] = Field(default=None)
    window_end: Optional[time] = Field(default=None)
    max_attempts: int = 3
    retry_minutes: int = 30
    timezone: str = "America/Guayaquil"
    config: dict = Field(default_factory=dict)

class CampaignUpdateIn(BaseModel):
    status: Optional[str] = None
    end_at: Optional[datetime] = None
    window_start: Optional[time] = None
    window_end: Optional[time] = None
    max_attempts: Optional[int] = None
    retry_minutes: Optional[int] = None
    timezone: Optional[str] = None
    config: Optional[dict] = None

class CampaignOut(BaseModel):
    campaign_id: int
    name: str
    campaign_type_id: int
    status: str
    start_at: datetime
    end_at: Optional[datetime]
    window_start: Optional[time]
    window_end: Optional[time]
    max_attempts: int
    retry_minutes: int
    timezone: str
    config: dict
    created_by: str
    created_at: datetime
