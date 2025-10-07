from typing import Any, Dict
from datetime import datetime, time
from app.core.domain.repositories.campaign_repository import CampaignRepository
from app.core.domain.errors import ValidationError, ConflictError

class CreateCampaign:
    def __init__(self, repo: CampaignRepository):
        self.repo = repo

    def __call__(self, data: Dict[str, Any]):
        # Normalizaciones simples
        data["name"] = data["name"].strip()

        # Reglas: tipo de campaña debe existir
        if not self.repo.campaign_type_exists(data["campaign_type_id"]):
            raise ValidationError("campaign_type_id does not exist")

        # Unicidad de nombre (negocio, para dar 409 explícito)
        if self.repo.get_by_name(data["name"]):
            raise ConflictError("campaign name already exists")

        # Ventanas / fechas coherentes (si vienen)
        ws: time | None = data.get("window_start")
        we: time | None = data.get("window_end")
        if ws is not None and we is not None and not (ws < we):
            raise ValidationError("window_start must be earlier than window_end")

        start: datetime = data["start_at"]
        end: datetime | None = data.get("end_at")
        if end is not None and end < start:
            raise ValidationError("end_at must be >= start_at")

        # Persistir
        return self.repo.create(data)
