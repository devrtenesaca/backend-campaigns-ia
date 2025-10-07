# backend/app/presentation/api/routers/campaign_contacts.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.domain.repositories.campaign_contact_repository import CampaignContactRepository
from app.presentation.api.dependencies_callbot import get_campaign_contact_repo
from app.presentation.api.dependencies_auth import get_current_claims, require_scopes
from app.core.domain.errors import ValidationError, ConflictError
from app.core.use_cases.enroll_contacts import EnrollContacts
from app.core.use_cases.enroll_contacts_csv import EnrollContactsCSV
from sqlalchemy.exc import IntegrityError
import logging

from app.security.auth import now_utc

router = APIRouter(prefix="/campaigns/{campaign_id}/contacts", tags=["campaign-contacts"])

@router.get("/list", dependencies=[Depends(require_scopes(["campaigns:read"]))])
def list_contacts(
    campaign_id: int,
    q: Optional[str] = Query(None),
    status_q: Optional[str] = Query(None, alias="status"),
    limit: int = 50,
    offset: int = 0,
    repo: CampaignContactRepository = Depends(get_campaign_contact_repo),
):
    return repo.list(campaign_id, q, status_q, limit, offset)

@router.post("/enroll", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_scopes(["campaigns:write"]))])
def create_contact(
    campaign_id: int,
    body: Dict[str, Any],
    repo: CampaignContactRepository = Depends(get_campaign_contact_repo),
    claims: Dict[str, Any] = Depends(get_current_claims),
):
    try:
        if not body.get("created_by"):
            body["created_by"] = claims.get("sub") or "system"
        return repo.create(campaign_id, body)
    except ValidationError as ex:
        raise HTTPException(status_code=422, detail=str(ex))
    except ConflictError as ex:
        raise HTTPException(status_code=409, detail=str(ex))

@router.put("/update", dependencies=[Depends(require_scopes(["campaigns:write"]))])
def upsert_contact(
    campaign_id: int,
    body: Dict[str, Any],
    repo: CampaignContactRepository = Depends(get_campaign_contact_repo),
    claims: Dict[str, Any] = Depends(get_current_claims),
):
    if not body.get("created_by"):
        body["created_by"] = claims.get("sub") or "system"
    
    body["updated_at"] = now_utc()
    return repo.upsert(campaign_id, body)

@router.delete("/delete/{campaign_contact_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_scopes(["campaigns:write"]))])
def delete_contact(
    campaign_id: int,
    campaign_contact_id: int,
    repo: CampaignContactRepository = Depends(get_campaign_contact_repo),
):
    repo.delete(campaign_contact_id)
    return

@router.post("/upload_csv", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_scopes(["campaigns:write"]))])
def upload_contacts_csv(
    campaign_id: int,
    body: Dict[str, str],
    repo: CampaignContactRepository = Depends(get_campaign_contact_repo),
    claims: Dict[str, Any] = Depends(get_current_claims),
):
    csv_base64 = body.get("csv_base64")
    if not csv_base64:
        raise HTTPException(status_code=422, detail="csv_base64 is required")
    if not body.get("created_by"):
        body["created_by"] = claims.get("sub") or "system"
    enroll_uc = EnrollContacts(repo)
    enroll_csv_uc = EnrollContactsCSV(enroll_uc)
    try:
        created_by = body.get("created_by", claims.get("sub") or "system")
        inserted, existing = enroll_csv_uc(campaign_id, csv_base64, created_by)
        return {"inserted": inserted, "existing": existing}
    except ValidationError as ex:
        raise HTTPException(status_code=422, detail=str(ex))
    except ConflictError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    except IntegrityError as ex:
        raise HTTPException(status_code=422, detail="Error de integridad en la base de datos: " + str(ex))
    except Exception as ex:
        logging.exception("Error inesperado en upload_contacts_csv")
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(ex))
