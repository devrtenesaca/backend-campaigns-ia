from datetime import datetime, timezone
from typing import Any, Dict, List
from jose import jwt
from passlib.context import CryptContext
from app.config.settings import get_settings
import hashlib
from secrets import token_urlsafe
import uuid

settings = get_settings()
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funciones de seguridad: hash de contraseñas y creación/verificación de JWT.

def hash_password(plain: str) -> str:
    return _pwd.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def create_access_token(sub: str, scopes: List[str] | None = None) -> str:
    iat = now_utc()
    exp = iat + settings.ACCESS_TTL
    payload: Dict[str, Any] = {
        "iss": settings.JWT_ISS,
        "aud": settings.JWT_AUD,
        "sub": sub,
        "scopes": scopes or [],
        "iat": int(iat.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALG)

def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALG],
        audience=settings.JWT_AUD,
        issuer=settings.JWT_ISS,
    )

def new_refresh_raw() -> str:
    """Genera un refresh token opaco (alto entropía)."""
    return token_urlsafe(64)

def hash_refresh(raw: str) -> str:
    """Se guarda el hash en DB para no persistir el valor en claro."""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()