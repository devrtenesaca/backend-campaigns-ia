# backend/app/infrastructure/repositories/campaign_repository_sqlalchemy.py
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
from sqlalchemy.exc import IntegrityError
from app.core.domain.entities.campaign import Campaign
from app.core.domain.repositories.campaign_repository import CampaignRepository
from app.infrastructure.db.callbot_campaigns import CampaignORM
from app.infrastructure.db.callbot_campaign_contacts import CampaignContactORM
from app.infrastructure.db.callbot_campaign_types import CampaignTypeORM
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, CheckViolation

from app.core.domain.errors import ConflictError, ValidationError, NotFoundError


def _to_domain(row: CampaignORM) -> Campaign:
    return Campaign(
        campaign_id=row.campaign_id,
        name=row.name,
        campaign_type_id=row.campaign_type_id,
        status=row.status,
        start_at=row.start_at,
        end_at=row.end_at,
        window_start=row.window_start,
        window_end=row.window_end,
        max_attempts=row.max_attempts,
        retry_minutes=row.retry_minutes,
        timezone=row.timezone,
        config=row.config or {},
        created_by=row.created_by,
        created_at=row.created_at,
    )


class CampaignRepositorySQLAlchemy(CampaignRepository):
    def __init__(self, db: Session):
        self.db = db

    def campaign_type_exists(self, campaign_type_id: int) -> bool:
        return (
            self.db.scalar(
                select(CampaignTypeORM.campaign_type_id).where(
                    CampaignTypeORM.campaign_type_id == campaign_type_id
                )
            )
            is not None
        )

    def create(self, data: Dict[str, Any]) -> Campaign:
        try:
            obj = CampaignORM(**data)
            self.db.add(obj)
            self.db.flush()
            self.db.refresh(obj)
            return _to_domain(obj)
        except IntegrityError as ex:
            orig = getattr(ex, "orig", None)
            if isinstance(orig, UniqueViolation):
                raise ConflictError("campaign name already exists") from ex
            if isinstance(orig, ForeignKeyViolation):
                raise ValidationError("invalid campaign_type_id") from ex
            if isinstance(orig, CheckViolation):
                raise ValidationError("constraint check failed") from ex
            raise

    def get(self, campaign_id: int) -> Optional[Campaign]:
        row = self.db.get(CampaignORM, campaign_id)
        return _to_domain(row) if row else None

    def get_by_name(self, name: str) -> Optional[Campaign]:
        row = self.db.scalars(
            select(CampaignORM).where(CampaignORM.name == name)
        ).first()
        return _to_domain(row) if row else None

    def list(self, q: Optional[str], limit: int, offset: int) -> List[Campaign]:
        stmt = select(CampaignORM).order_by(CampaignORM.campaign_id.desc())
        if q:
            stmt = stmt.where(CampaignORM.name.ilike(f"%{q}%"))
        rows = self.db.scalars(stmt.limit(limit).offset(offset)).all()
        return [_to_domain(r) for r in rows]

    def update(self, campaign_id: int, data: Dict[str, Any]) -> Campaign:
        try:
            self.db.execute(
                update(CampaignORM)
                .where(CampaignORM.campaign_id == campaign_id)
                .values(**data)
            )
            row = self.db.get(CampaignORM, campaign_id)
            if not row:
                return # el use case ya valida existencia
            return _to_domain(row)
        except IntegrityError as ex:
            orig = getattr(ex, "orig", None)
            if isinstance(orig, UniqueViolation):
                raise ConflictError("campaign name already exists") from ex
            if isinstance(orig, CheckViolation):
                raise ValidationError("constraint check failed") from ex
            raise

    def delete(self, campaign_id: int) -> None:
        row = self.db.get(CampaignORM, campaign_id)
        if not row:
            return  # el use case ya valida existencia
        try:
            self.db.delete(row)
            self.db.flush()  # asegura que se ejecute y dispare FK si aplica
        except IntegrityError as ex:
            # Si hay dependencias (p.ej., calls → campaign_contacts → campaign), Postgres lanza FK violation
            if isinstance(getattr(ex, "orig", None), ForeignKeyViolation):
                raise ConflictError(
                    "Cannot delete campaign with related records"
                ) from ex
            raise