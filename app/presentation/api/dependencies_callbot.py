# backend/app/presentation/api/dependencies_callbot.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_session
from app.infrastructure.repositories.campaign_repository_sqlalchemy import CampaignRepositorySQLAlchemy
from app.infrastructure.repositories.campaign_contact_repository_sqlalchemy import CampaignContactRepositorySQLAlchemy


def get_db(db: Session = Depends(get_session)):
    return db

def get_campaign_repo(db: Session = Depends(get_db)):
    return CampaignRepositorySQLAlchemy(db)

def get_campaign_contact_repo(db: Session = Depends(get_db)):
    return CampaignContactRepositorySQLAlchemy(db)