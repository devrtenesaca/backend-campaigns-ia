# backend/app/infraestructure/repositories/campaign_contact_repository_sqlalchemy.py
from __future__ import annotations

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation, CheckViolation, ForeignKeyViolation

from app.core.domain.entities.campaign_contact import CampaignContact
from app.core.domain.repositories.campaign_contact_repository import CampaignContactRepository
from app.core.domain.errors import NotFoundError, ValidationError, ConflictError

from app.infrastructure.db.callbot_campaign_contacts import CampaignContactORM

def _to_domain(row: CampaignContactORM) -> CampaignContact:
    return CampaignContact(
        campaign_contact_id=row.campaign_contact_id,
        campaign_id=row.campaign_id,
        phone=row.phone,
        name=row.name,
        attributes=row.attributes or {},
        status=row.status,
        attempt_count=row.attempt_count,
        next_attempt_at=row.next_attempt_at,
        last_disposition=row.last_disposition,
        last_error=row.last_error,
        notes=row.notes,
        source_batch_id=row.source_batch_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        created_by=row.created_by
    )

def _merge_dicts(base: Optional[dict], patch: Optional[dict]) -> dict:
    base = base or {}
    patch = patch or {}
    return {**base, **patch}  # reemplazo superficial; ajusta si quieres deep-merge

class CampaignContactRepositorySQLAlchemy(CampaignContactRepository):
    def __init__(self, db: Session):
        self.db = db


    def contact_exists(self, contact_id: int) -> bool:
        return self.db.scalar(
            select(CampaignContactORM.contact_id).where(CampaignContactORM.contact_id == contact_id)
        ) is not None

    def exists_in_campaign(self, campaign_id: int, contact_id: int) -> bool:
        return self.db.scalar(
            select(CampaignContactORM.campaign_id).where(
                CampaignContactORM.campaign_id == campaign_id,
                CampaignContactORM.contact_id == contact_id
            )
        ) is not None

    # ---------- READ ----------
    def get(self, campaign_contact_id: int) -> Optional[CampaignContact]:
        row = self.db.get(CampaignContactORM, campaign_contact_id)
        return _to_domain(row) if row else None

    def get_by_phone(self, campaign_id: int, phone: str) -> Optional[CampaignContact]:
        row = self.db.scalars(
            select(CampaignContactORM).where(
                CampaignContactORM.campaign_id == campaign_id,
                CampaignContactORM.phone == phone
            )
        ).first()
        return _to_domain(row) if row else None

    def list(
        self,
        campaign_id: int,
        q: Optional[str],
        status: Optional[str],
        limit: int,
        offset: int
    ) -> List[CampaignContact]:
        stmt = select(CampaignContactORM).where(CampaignContactORM.campaign_id == campaign_id)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                (CampaignContactORM.phone.ilike(like)) |
                (CampaignContactORM.name.ilike(like))
            )
        if status:
            stmt = stmt.where(CampaignContactORM.status == status)
        stmt = stmt.order_by(CampaignContactORM.campaign_contact_id.desc()).limit(limit).offset(offset)
        rows = self.db.scalars(stmt).all()
        return [_to_domain(r) for r in rows]

    # ---------- WRITE ----------
    def create(self, campaign_id: int, data: Dict[str, Any]) -> CampaignContact:
        # phone es obligatorio
        phone = (data.get("phone") or "").strip()
        if not phone:
            raise ValidationError("phone is required")

        # Validar si ya existe antes de crear
        exists = self.db.scalars(
            select(CampaignContactORM).where(
                CampaignContactORM.campaign_id == campaign_id,
                CampaignContactORM.phone == phone
            )
        ).first()
        if exists:
            raise ConflictError(f"Contact with phone '{phone}' already exists for this campaign.")

        try:
            row = CampaignContactORM(
                campaign_id=campaign_id,
                phone=phone,
                name=data.get("name"),
                attributes=data.get("attributes") or {},
                status=data.get("status") or "Pending",
                attempt_count=data.get("attempt_count") or 0,
                next_attempt_at=data.get("next_attempt_at"),
                last_disposition=data.get("last_disposition"),
                last_error=data.get("last_error"),
                notes=data.get("notes"),
                source_batch_id=data.get("source_batch_id"),
                created_by=data.get("created_by") or "system",
            )
            self.db.add(row)
            self.db.flush()
            self.db.refresh(row)
            return _to_domain(row)
        except IntegrityError as ex:
            orig = getattr(ex, "orig", None)
            if isinstance(orig, UniqueViolation):
                # UNIQUE(campaign_id, phone)
                raise ConflictError(f"Contact with phone '{phone}' already exists for this campaign.") from ex
            if isinstance(orig, ForeignKeyViolation):
                raise ValidationError(f"El campaign_id {campaign_id} no existe en la tabla campaigns") from ex
            if isinstance(orig, CheckViolation):
                raise ValidationError("constraint check failed") from ex
            raise

    def upsert(self, campaign_id: int, data: Dict[str, Any]) -> CampaignContact:
        phone = (data.get("phone") or "").strip()
        if not phone:
            raise ValidationError("phone is required")
        # ¿Existe?
        existing = self.db.scalars(
            select(CampaignContactORM).where(
                CampaignContactORM.campaign_id == campaign_id,
                CampaignContactORM.phone == phone
            )
        ).first()
        if not existing:
            return self.create(campaign_id, data)

        # Actualiza (política: merge superficial en dicts)
        changes = dict(data)
        if "attributes" in changes:
            changes["attributes"] = _merge_dicts(existing.attributes, changes["attributes"])
        
        for k, v in changes.items():
            if v is not None and hasattr(existing, k):
                setattr(existing, k, v)
        self.db.flush()
        self.db.refresh(existing)
        return _to_domain(existing)

    def bulk_upsert(self, campaign_id: int, items: List[Dict[str, Any]]) -> Tuple[int, int]:
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        inserted = existing = 0
        for it in items:
            logger.info(f"🔍 Processing item for bulk_upsert: {it}")
            logger.info(f"🔍 Item attributes: {it.get('attributes')} (type: {type(it.get('attributes'))})")
            
            phone = (it.get("phone") or "").strip()
            if not phone:
                continue
            row = self.db.scalars(
                select(CampaignContactORM).where(
                    CampaignContactORM.campaign_id == campaign_id,
                    CampaignContactORM.phone == phone
                )
            ).first()
            if row:
                # opcional: merge de atributos/datos
                if it.get("attributes"):
                    logger.info(f"🔄 Updating existing contact attributes from {row.attributes} to {it['attributes']}")
                    row.attributes = _merge_dicts(row.attributes, it["attributes"])
                # Actualiza campos simples si vienen
                for k in ("name", "notes", "status", "next_attempt_at", "last_disposition", "last_error"):
                    if it.get(k) is not None:
                        setattr(row, k, it[k])
                existing += 1
            else:
                attributes_to_save = it.get("attributes") or {}
                logger.info(f"➕ Creating new contact with attributes: {attributes_to_save} (type: {type(attributes_to_save)})")
                
                new_contact = CampaignContactORM(
                    campaign_id=campaign_id,
                    phone=phone,
                    name=it.get("name"),
                    attributes=attributes_to_save,
                    status=it.get("status") or "Pending",
                    source_batch_id=it.get("source_batch_id"),
                    created_by=it.get("created_by") or "system",
                )
                logger.info(f"📝 ORM object created with attributes: {new_contact.attributes}")
                self.db.add(new_contact)
                self.db.flush()  # Forzar flush para ver el estado
                logger.info(f"🔄 After flush, attributes: {new_contact.attributes}")
                inserted += 1
        # flush lo hace la dependency transaccional cuando corresponda; aquí podemos dejarlo implícito
        return inserted, existing

    def update(self, campaign_contact_id: int, changes: Dict[str, Any]) -> CampaignContact:
        row = self.db.get(CampaignContactORM, campaign_contact_id)
        if not row:
            raise NotFoundError("Campaign contact not found")
        try:
            # merges para dicts
            if "attributes" in changes and changes["attributes"] is not None:
                row.attributes = _merge_dicts(row.attributes, changes["attributes"])
                changes.pop("attributes", None)
            for k, v in changes.items():
                if v is not None and hasattr(row, k):
                    setattr(row, k, v)
            self.db.flush()
            self.db.refresh(row)
            return _to_domain(row)
        except IntegrityError as ex:
            orig = getattr(ex, "orig", None)
            if isinstance(orig, UniqueViolation):
                raise ConflictError("contact already exists for this campaign") from ex
            if isinstance(orig, CheckViolation):
                raise ValidationError("constraint check failed") from ex
            raise

    def delete(self, campaign_contact_id: int) -> None:
        row = self.db.get(CampaignContactORM, campaign_contact_id)
        if not row:
            return
        try:
            self.db.delete(row)
            self.db.flush()
        except IntegrityError as ex:
            if isinstance(getattr(ex, "orig", None), ForeignKeyViolation):
                # Hay calls asociados con ON DELETE RESTRICT
                raise ConflictError("Cannot delete contact with related calls") from ex
            raise
