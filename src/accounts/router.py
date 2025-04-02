from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from src.accounts.model import UserModel
from src.accounts.service import UserService
from src.accounts.schemas import ROLE_ADMIN, UserSchema, UserUpdate
from src.core.db_helper import db
from src.dependencies import get_current_role, http_bearer, get_current_auth_access


router = APIRouter(
    prefix="/Accounts", 
    tags=["Accounts"],
    dependencies=[Depends(http_bearer)]
)


@router.get("/Me", response_model=UserSchema)
async def get_user_info(
    user: UserModel = Depends(get_current_auth_access),
    session: AsyncSession = Depends(db.session_dependency)
):
    return await UserService.get_user(user_id=user.id, session=session)


@router.put("/Update", response_model=UserSchema)
async def update_user_info(
    user_update: UserUpdate,
    user: UserModel = Depends(get_current_auth_access),
    session: AsyncSession = Depends(db.session_dependency)
):
    return await UserService.update_user(user_id=user.id, user=user_update, session=session)


@router.delete("/{id}")
async def delete_user_only_admin(
    id: uuid.UUID,
    user: UserModel = Depends(get_current_auth_access),
    session: AsyncSession = Depends(db.session_dependency)
):
    await get_current_role([ROLE_ADMIN], user)
    await UserService.delete_user(user_id=id, session=session)