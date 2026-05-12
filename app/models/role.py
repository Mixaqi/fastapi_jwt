from enum import Enum

from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Role(Enum):
    USER = "user"
    STAFF = "staff"
    SUPERUSER = "superuser"


class RoleModel(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Role] = mapped_column(SqlAlchemyEnum(Role), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)