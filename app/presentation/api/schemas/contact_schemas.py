# backend/app/presentation/api/schemas/contact_schemas.py
from pydantic import BaseModel
from typing import Optional

class ContactUpsertIn(BaseModel):
    phone: str
    name: Optional[str] = None
    attributes: dict = {}
    created_by: str

class ContactOut(BaseModel):
    contact_id: int
    phone: str
    name: Optional[str]
    attributes: dict
    created_by: str
