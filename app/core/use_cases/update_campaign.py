from app.core.domain.repositories.campaign_repository import CampaignRepository
from app.core.domain.entities.campaign import Campaign
from app.core.domain.errors import NotFoundError, ValidationError, ConflictError

class UpdateCampaign:
    def __init__(self, repo: CampaignRepository):
        self.repo = repo

    def __call__(self, campaign_id: int, data: dict) -> Campaign:
        if not data:
            raise ValidationError("No data to update")
        # Validar existencia antes de actualizar
        obj = self.repo.get(campaign_id)
        if not obj:
            raise NotFoundError("Campaign not found")
        return self.repo.update(campaign_id, data)