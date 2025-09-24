# app/infrastructure/repositories/user_repository_sqlalchemy.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.domain.entities.user import User
from app.core.domain.repositories.user_repository import UserRepository

from app.infrastructure.db.users import UserORM
from app.infrastructure.db.roles import RoleORM
from app.infrastructure.db.scopes import ScopeORM
from app.infrastructure.db.role_scopes import RoleScopeORM
from app.infrastructure.db.user_roles import UserRoleORM


class UserRepositorySQLAlchemy(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def _scopes_for(self, user_id: int) -> list[str]:
        stmt = (
            select(ScopeORM.name)
            .join(RoleScopeORM, RoleScopeORM.scope_id == ScopeORM.id)
            .join(RoleORM, RoleScopeORM.role_id == RoleORM.id)
            .join(UserRoleORM, UserRoleORM.role_id == RoleORM.id)
            .where(UserRoleORM.user_id == user_id)
        )
        return [row[0] for row in self.db.execute(stmt).all()]

    def _roles_for(self, user_id: int) -> list[str]:
        stmt = (
            select(RoleORM.name)
            .join(UserRoleORM, UserRoleORM.role_id == RoleORM.id)
            .where(UserRoleORM.user_id == user_id)
        )
        return [row[0] for row in self.db.execute(stmt).all()]

    def get_by_email(self, email: str) -> Optional[tuple[User, str]]:
        orm = self.db.execute(
            select(UserORM).where(UserORM.email == email)
        ).scalar_one_or_none()

        if not orm:
            return None

        scopes = self._scopes_for(orm.id)
        roles = self._roles_for(orm.id)

        dom = User(
            id=orm.id,
            username=orm.username,
            email=orm.email,
            is_active=orm.is_active,
            must_change_pw=orm.must_change_pw,
            scopes=scopes,
            roles=roles,
        )
        return dom, orm.hashed_password
