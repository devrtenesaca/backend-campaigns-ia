# backend/app/core/domain/repositories/campaign_contact_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from app.core.domain.entities.campaign_contact import CampaignContact

class CampaignContactRepository(ABC):
    """Repositorio de contactos de campañas."""

    # Lectura
    @abstractmethod
    def get(self, campaign_contact_id: int) -> Optional[CampaignContact]: ...
    
    @abstractmethod
    def get_by_phone(self, campaign_id: int, phone: str) -> Optional[CampaignContact]: ...
    
    @abstractmethod
    def list(
        self,
        campaign_id: int,
        q: Optional[str],
        status: Optional[str],
        limit: int,
        offset: int
    ) -> List[CampaignContact]: ...

    # Escritura
    @abstractmethod
    def create(self, campaign_id: int, data: Dict[str, Any]) -> CampaignContact:
        """
        data: {phone (req), name?, attributes?,source_batch_id? ...}
        Debe respetar UNIQUE(campaign_id, phone).
        """
        ...
    
    @abstractmethod
    def upsert(self, campaign_id: int, data: Dict[str, Any]) -> CampaignContact:
        """
        Si (campaign_id, phone) existe → actualiza campos (merge/replace según política).
        Si no existe → crea.
        """
        ...
    
    @abstractmethod
    def bulk_upsert(self, campaign_id: int, items: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Inserta/actualiza en lote. Devuelve (inserted, existing).
        items: [{"phone": "...", "name": "...", "attributes": {...}}, ...]
        """
        ...
    
    @abstractmethod
    def update(self, campaign_contact_id: int, changes: Dict[str, Any]) -> CampaignContact: ...
    
    @abstractmethod
    def delete(self, campaign_contact_id: int) -> None: ...
