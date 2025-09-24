from __future__ import annotations
from typing import Optional, Protocol
from app.core.domain.entities.user import User

class UserRepository(Protocol):
    """
    Puerto del dominio para acceder a usuarios.
    No conoce SQLAlchemy ni Postgres. Solo tipos del dominio.
    """

    def get_by_email(self, email: str) -> Optional[tuple[User, str]]:
        """
        Busca un usuario por email.

        Returns:
            (User, hashed_password) si existe, o None si no existe.
            - User: entidad de dominio con scopes efectivos.
            - hashed_password: hash de contraseña (bcrypt) para validar login.
        """
        ...

    def get_by_username(self, username: str) -> Optional[tuple[User, str]]:
        """
        Busca un usuario por username.

        Returns:
            (User, hashed_password) si existe, o None.
        """
        ...

