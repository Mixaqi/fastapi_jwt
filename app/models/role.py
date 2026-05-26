from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SqlAlchemyEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


if TYPE_CHECKING:
    from app.models.user import UserModel


class Role(Enum):
    USER = "user"
    STAFF = "staff"
    SUPERUSER = "superuser"


class RoleModel(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Role] = mapped_column(SqlAlchemyEnum(Role), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    users: Mapped[list["UserModel"]] = relationship(
        secondary="users_roles",
        back_populates="roles",
    )
