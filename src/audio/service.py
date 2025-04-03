import os
import shutil
import uuid
import mimetypes
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.audio.dao import AudioDAO
from src.audio.model import AudioModel
from src.audio.schemas import AudioCreate, Audio
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
        if not file:
            raise HTTPException(
                status_code=400, 
                detail="file not found"
            )
    
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
                file_path=f"{str(settings.audio_path)}/{name}",
                user_id=user_id,
            )
        )

        extension = mimetypes.guess_extension(file.content_type) or ""

        try:
            file_path = os.path.join(settings.audio_path, f"{name}{extension}")

            with open(file_path, "wb") as f:
                f.write(await file.read())

            await session.commit()

            return Audio(
                filename=name,
                file_path=file_path
            )
        except Exception as e: 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e
            )
        
    
    @classmethod
    async def get_all_user_audios(
        cls,
        user_id: uuid.UUID,
        offset: int, 
        limit: int, 
        session: AsyncSession
    ):
        return await AudioDAO.find_all(
            session,
            AudioModel.user_id == user_id,
            offset=offset,
            limit=limit
        )
