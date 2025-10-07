# app/core/use_cases/enroll_contacts.py
from typing import List, Dict, Tuple, Any
from app.core.domain.repositories.campaign_contact_repository import CampaignContactRepository
from app.core.domain.errors import ValidationError
import re

class EnrollContacts:
    """
    Alta/actualización masiva de contactos por campaña con validaciones previas.
    - Requiere 'phone' no vacío (string).
    - Deduplica por phone dentro del mismo lote.
    - 'attributes' debe ser dict (se fuerza {} si None).
    - Opcional: recorta longitudes de 'name'.
    """
    _PHONE_RE = re.compile(r"\+?\d{7,25}")  # simple: + y de 7 a 25 dígitos

    def __init__(self, repo: CampaignContactRepository):
        self.repo = repo

    def __call__(self, campaign_id: int, contacts: List[Dict[str, Any]], created_by: str = "system") -> Tuple[int, int]:
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not isinstance(contacts, list) or not contacts:
            raise ValidationError("No contacts provided")

        logger.info(f"🔍 EnrollContacts received {len(contacts)} contacts")
        for i, contact in enumerate(contacts):
            logger.info(f"📥 Input contact {i+1}: {contact}")
            logger.info(f"📥 Input attributes: {contact.get('attributes')} (type: {type(contact.get('attributes'))})")

        cleaned: List[Dict[str, Any]] = []
        seen_phones: set[str] = set()

        for idx, raw in enumerate(contacts, start=1):
            if not isinstance(raw, dict):
                raise ValidationError(f"Item {idx} must be an object")

            phone = raw.get("phone")
            # normaliza a string y trim
            if phone is None:
                # lo ignoramos silenciosamente o puedes levantar error explícito:
                # raise ValidationError(f"Item {idx}: 'phone' is required")
                continue
            if not isinstance(phone, str):
                phone = str(phone)
            phone = phone.strip()
            if not phone:
                continue

            # valida formato básico de teléfono
            if not self._PHONE_RE.fullmatch(phone):
                raise ValidationError(f"Item {idx}: invalid phone format '{phone}'")

            # dedupe dentro del mismo lote
            if phone in seen_phones:
                continue
            seen_phones.add(phone)

            # attributes debe ser dict
            attributes = raw.get("attributes")
            logger.info(f"🔄 Processing item {idx} attributes: {attributes} (type: {type(attributes)})")
            
            if attributes is None:
                attributes = {}
                logger.warning(f"⚠️ Item {idx}: attributes was None, setting to empty dict")
            elif not isinstance(attributes, dict):
                logger.error(f"❌ Item {idx}: attributes is not a dict: {type(attributes)}")
                raise ValidationError(f"Item {idx}: 'attributes' must be an object")

            name = raw.get("name") or None
            if isinstance(name, str):
                name = name.strip() or None
                if name and len(name) > 120:
                    name = name[:120]

            cleaned_item = {
                "phone": phone,
                "name": name,
                "attributes": attributes,
                "created_by": created_by
            }
            logger.info(f"✅ Cleaned item {idx}: {cleaned_item}")
            logger.info(f"✅ Cleaned attributes: {cleaned_item['attributes']} (type: {type(cleaned_item['attributes'])})")
            cleaned.append(cleaned_item)

        if not cleaned:
            raise ValidationError("No valid contacts to enroll")

        logger.info(f"📤 Sending {len(cleaned)} cleaned contacts to repository")
        for i, contact in enumerate(cleaned):
            logger.info(f"📤 Final contact {i+1}: {contact}")

        # delega al repo (ya validado y deduplicado)
        # bulk_upsert debe devolver (inserted, existing) y no lanzar ConflictError
        return self.repo.bulk_upsert(campaign_id, cleaned)
