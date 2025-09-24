from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class User:
    """
    Entidad de dominio (pura, sin SQLAlchemy ni Pydantic).
    Representa a un usuario del sistema.
    """
    id: int
    username: str
    email: Optional[str]
    is_active: bool
    must_change_pw: bool
    # Permisos efectivos (derivados de roles -> scopes)
    scopes: list[str]
    # (Opcional) roles para trazabilidad / auditoría
    roles: list[str] | None = None
