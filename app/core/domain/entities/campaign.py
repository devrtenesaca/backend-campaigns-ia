# backend/app/core/domain/entities/campaign.py
from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional

@dataclass(frozen=True)
class Campaign:
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
