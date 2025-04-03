from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession


from src.accounts.model import UserModel
from src.audio.service import AudioService
from src.audio.schemas import AudioSchema
from src.core.config import settings
from src.core.db_helper import db
from src.dependencies import http_bearer, get_current_auth_access


router = APIRouter(
    prefix="/Audio", 
    tags=["Audio"],
)


@router.post("/UploadFile")
async def upload_file(
    file: UploadFile = File(...),
    name: str = Query(..., description="File name"),
    user: UserModel = Depends(get_current_auth_access),
    session: AsyncSession = Depends(db.session_dependency)
):
    return await AudioService.upload_file(
        file=file,
        name=name,
        user_id=user.id,
        session=session
    )


@router.get("/GetAllUserAudios", response_model=list[AudioSchema])
async def get_all_user_audios(
    offset: int,
    count: int,
    user: UserModel = Depends(get_current_auth_access),
    session: AsyncSession = Depends(db.session_dependency)
):
    """
    offset - с какого элемента будет отображаться список.\n
    limit - количество отображаемых элементов
    """
    return await AudioService.get_all_user_audios(
        session=session,
        offset=offset, 
        limit=count,
        user_id=user.id
    )