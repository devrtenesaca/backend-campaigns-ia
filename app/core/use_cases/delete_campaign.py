# backend/app/core/use_cases/delete_campaign.py
from app.core.domain.repositories.campaign_repository import CampaignRepository
from app.core.domain.errors import NotFoundError, ConflictError

class DeleteCampaign:
    def __init__(self, repo: CampaignRepository):
        self.repo = repo

    def __call__(self, campaign_id: int, *, force: bool = False) -> None:
        # 1) Debe existir
        current = self.repo.get(campaign_id)
        if not current:
            raise NotFoundError("Campaign not found")

        # 2) Reglas de negocio (opcional): no permitir borrar activas/pausadas
        if not force and current.status in {"Active", "Paused"}:
            raise ConflictError(f"Cannot delete campaign in status {current.status}")

        # 3) Persistencia
        self.repo.delete(campaign_id)
