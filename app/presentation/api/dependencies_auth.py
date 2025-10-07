from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.security.auth import decode_access_token
from app.infrastructure.db.session import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Guardias y dependencias para rutas protegidas.

def get_db(db: Session = Depends(get_session)):
    return db

def get_current_claims(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_access_token(token)
        return {"sub": payload.get("sub"), "scopes": payload.get("scopes", [])}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def require_scopes(required: list[str]):
    def _dep(claims = Depends(get_current_claims)):
        scopes = set(claims.get("scopes", []))
        missing = [s for s in required if s not in scopes]
        if missing:
            raise HTTPException(status_code=403, detail=f"Faltan scopes: {missing}")
        return claims
    return _dep

