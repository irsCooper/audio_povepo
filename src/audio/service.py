import os
import shutil
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from audio_povepo.src.audio.dao import AudioDAO
from audio_povepo.src.audio.model import AudioModel
from audio_povepo.src.audio.schemas import AudioCreate
from src.core.config import settings

class AudioService:
    @classmethod
    async def upload_file(
        cls,
        file: UploadFile,
        name: str,
        user_id: uuid.UUID,
        session: AsyncSession
    ):
        audio: AudioModel = await AudioDAO.find_one_or_none(
            session,
            AudioModel.filename == name
        )

        if audio:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="choose a different name"
            )
        
        await AudioDAO.add(
            session,
            obj_in=AudioCreate(
                filename=name,
                file_path=f"{str(settings.audio_path)}/name",
                user_id=user_id,
            )
        )

        file_path = os.path.join(settings.audio_path, name)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        await session.commit()

        # TODO
