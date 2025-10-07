# backend/app/core/domain/entities/campaign_contact.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class CampaignContact:
    campaign_contact_id: int
    campaign_id: int
    phone: str
    name: Optional[str]
    attributes: Dict[str, Any]
    status: str                 # 'Pending' | 'Dialing' | 'Finished' | 'Error' | 'Excluded'
    attempt_count: int
    next_attempt_at: Optional[datetime]
    last_disposition: Optional[str]
    last_error: Optional[str]
    notes: Optional[str]
    source_batch_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: str

