from fastapi import APIRouter, Depends
from app.presentation.api.dependencies_auth import get_current_claims, require_scopes

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def get_me(claims = Depends(get_current_claims)):
    """
    Devuelve el perfil del usuario autenticado (sub + scopes).
    """
    return {
        "email": claims["sub"],
        "scopes": claims.get("scopes", [])
    }

@router.get("/", dependencies=[Depends(require_scopes(["users:read"]))])
def list_users():
    """
    Ejemplo de ruta protegida: solo accesible si el usuario
    tiene el scope 'users:read'.
    """
    return {"items": []}

