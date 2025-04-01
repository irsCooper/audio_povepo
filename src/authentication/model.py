from datetime import datetime
import uuid
from sqlalchemy import TIMESTAMP, UUID, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.base_model import BaseModel

class RefreshModel(BaseModel):
    __tablename__ = 'refresh_session'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    expire_in: Mapped[int]  = mapped_column(Integer, nullable=False)
    creates_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    yandex_session: Mapped["YandexSession"] = relationship(
        "YandexSession",
        back_populates="refresh_session",
        uselist=False
    )


class YandexSession(BaseModel):
    __tablename__ = "yandex_session"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    expire_in: Mapped[int]  = mapped_column(Integer, nullable=False)
    creates_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    refresh_session_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("refresh_session.id", ondelete="CASCADE"), nullable=False)
    
    refresh_session: Mapped["RefreshModel"] = relationship(
        "RefreshModel",
        back_populates="yandex_session",
        uselist=False
    )