from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserPageHistoryModel(Base):
    __tablename__ = "user_page_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    page_id: Mapped[int] = mapped_column(nullable=False, index=True)

    viewed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
