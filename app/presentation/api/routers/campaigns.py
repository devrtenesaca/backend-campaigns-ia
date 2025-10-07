# backend/app/presentation/api/routers/campaigns.py
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.presentation.api.schemas.campaign_schemas import (
    CampaignCreateIn,
    CampaignUpdateIn,
    CampaignOut,
)
from app.presentation.api.dependencies_callbot import (
    get_campaign_repo,
    get_campaign_contact_repo,
)
from app.core.domain.repositories.campaign_repository import CampaignRepository
from app.core.domain.repositories.campaign_contact_repository import CampaignContactRepository
from app.presentation.api.dependencies_callbot import get_db
from app.presentation.api.dependencies_auth import get_current_claims, require_scopes
from psycopg2.errors import UniqueViolation

from app.core.use_cases.create_campaign import CreateCampaign
from app.core.use_cases.update_campaign import UpdateCampaign
from app.core.use_cases.delete_campaign import DeleteCampaign

from app.core.domain.errors import ValidationError, ConflictError, NotFoundError
from sqlalchemy.exc import SQLAlchemyError

import csv, io

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post(
    "/create",
    response_model=CampaignOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_scopes(["campaigns:write"]))],
)
def create_campaign(
    payload: CampaignCreateIn,
    repo: CampaignRepository = Depends(get_campaign_repo),
    claims: Dict[str, Any] = Depends(get_current_claims),
):
    data = payload.model_dump()
    if not data.get("created_by"):
        data["created_by"] = claims.get("sub") or "system"
    try:
        return CreateCampaign(repo)(data)
    except ValidationError as ex:
        raise HTTPException(status_code=422, detail=str(ex))
    except ConflictError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch(
    "/update/{campaign_id}",
    response_model=CampaignOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_scopes(["campaigns:write"]))],
)
def update_campaign(
    campaign_id: int,
    payload: CampaignUpdateIn,
    repo: CampaignRepository = Depends(get_campaign_repo),
    db: Session = Depends(get_db),
):
    try:
        obj = UpdateCampaign(repo)(
            campaign_id,
            {k: v for k, v in payload.model_dump().items() if v is not None},
        )
        return obj
    except NotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except ValidationError as ex:
        raise HTTPException(status_code=422, detail=str(ex))
    except ConflictError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    except Exception as ex:
        import traceback
        print("--- Exception in update_campaign ---")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.delete(
    "/delete/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_scopes(["campaigns:write"]))],
)
def delete_campaign(
    campaign_id: int,
    repo: CampaignRepository = Depends(get_campaign_repo),
):
    try:
        DeleteCampaign(repo)(campaign_id)
        return  # 204
    except NotFoundError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))
    except ConflictError as ex:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ex))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/list/{campaign_id}", 
            response_model=CampaignOut,
            dependencies=[Depends(require_scopes(["campaigns:read"]))],
            )
def get_campaign(
    campaign_id: int, repo: CampaignRepository = Depends(get_campaign_repo)
):
    obj = repo.get(campaign_id)
    if not obj:
        raise HTTPException(404, "Campaign not found")
    return obj


@router.get("/all", 
            response_model=List[CampaignOut],
            dependencies=[Depends(require_scopes(["campaigns:read"]))],
            )
def list_campaigns(
    q: Optional[str] = Query(None),
    limit: int = 50,
    offset: int = 0,
    repo: CampaignRepository = Depends(get_campaign_repo),
):
    return repo.list(q, limit, offset)
