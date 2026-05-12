from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey

from app.models.base import Base


class UserRoleModel(Base):
    __tablename__ = "users_roles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)