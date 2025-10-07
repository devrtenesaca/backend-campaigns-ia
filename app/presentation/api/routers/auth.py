# app/presentation/api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.presentation.api.schemas.auth_schemas import LoginIn, RefreshIn, TokenPairOut

from app.presentation.api.dependencies_auth import get_db
from app.security.auth import (
    verify_password,
    create_access_token,
    new_refresh_raw,
    hash_refresh,
    now_utc,
)
from app.infrastructure.repositories.user_repository_sqlalchemy import UserRepositorySQLAlchemy
from app.infrastructure.db.users import UserORM
from app.infrastructure.db.refresh_tokens import RefreshTokenORM
from app.config.settings import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


# ---------- Endpoints ----------
@router.post("/login", response_model=TokenPairOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    repo = UserRepositorySQLAlchemy(db)
    found = repo.get_by_email(body.email)
    if not found:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    user, hashed = found
    if not user.is_active or not verify_password(body.password, hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    # Access con scopes efectivos
    access = create_access_token(sub=user.email or user.username, scopes=user.scopes)

    # Refresh opaco: generar, hashear y guardar
    raw_refresh = new_refresh_raw()
    db.add(RefreshTokenORM(
        user_id=user.id,
        token_hash=hash_refresh(raw_refresh),
        expires_at=now_utc() + settings.REFRESH_TTL
    ))

    return TokenPairOut(access_token=access, refresh_token=raw_refresh)


@router.post("/refresh", response_model=TokenPairOut)
def refresh(body: RefreshIn, db: Session = Depends(get_db)):
    """
    Valida el refresh recibido, lo rota, y emite un nuevo access token.
    **Recalcula scopes reales** del usuario (roles -> scopes) antes de firmar el access.
    """
    # 1) Usuario válido y activo
    orm_user = db.execute(
        select(UserORM).where(UserORM.email == body.email)
    ).scalar_one_or_none()
    if not orm_user or not orm_user.is_active:
        raise HTTPException(status_code=401, detail="Usuario inválido")

    # 2) Refresh válido: mismo usuario, no revocado, no expirado
    hashed = hash_refresh(body.refresh_token)
    rt = db.execute(
        select(RefreshTokenORM).where(
            RefreshTokenORM.user_id == orm_user.id,
            RefreshTokenORM.token_hash == hashed,
            RefreshTokenORM.revoked_at.is_(None),
            RefreshTokenORM.expires_at > now_utc(),
        )
    ).scalar_one_or_none()
    if not rt:
        raise HTTPException(status_code=401, detail="Refresh inválido o expirado")

    # 3) Rotación de refresh: revoca el anterior
    rt.revoked_at = now_utc()

    # 4) Recalcular permisos actuales (roles -> scopes) con el repositorio
    repo = UserRepositorySQLAlchemy(db)
    found = repo.get_by_email(body.email)
    if not found:
        # Esto no debería pasar si llegó hasta aquí, pero lo chequeamos por seguridad
        raise HTTPException(status_code=401, detail="Usuario inválido")
    user, _ = found

    # 5) Emitir nuevo access con scopes actuales
    new_access = create_access_token(sub=user.email or user.username, scopes=user.scopes)

    # 6) Generar y persistir nuevo refresh (opaco, hasheado)
    new_raw_refresh = new_refresh_raw()
    db.add(RefreshTokenORM(
        user_id=user.id,
        token_hash=hash_refresh(new_raw_refresh),
        expires_at=now_utc() + settings.REFRESH_TTL
    ))
    return TokenPairOut(access_token=new_access, refresh_token=new_raw_refresh)
