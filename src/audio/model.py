import uuid
from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.base_model import BaseModel


class AudioModel(BaseModel):
    __tablename__ = 'audio_session'

    filename: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
