from typing import Optional
import uuid

from fastapi import HTTPException, status
from sqlalchemy import and_ 

from src.accounts.schemas import UserUpdate, UserCreate
from src.accounts.model import UserModel
from src.accounts.dao import UserDAO

from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    @classmethod
    async def create_user(
        cls,
        user_in: UserCreate,
        session: AsyncSession
    ) -> Optional[UserModel]:
        return await UserDAO.add(
            session=session,
            obj_in=UserCreate(
                **user_in.model_dump(),
            )
        )
    

    @classmethod
    async def get_user(
        cls, 
        user_id: uuid.UUID, 
        session: AsyncSession
    ) -> UserModel:
        user = await UserDAO.find_one_or_none(
            session,
            UserModel.id == user_id,
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    

    @classmethod
    async def update_user(
        cls,
        user_id: uuid.UUID,
        user: UserUpdate,
        session: AsyncSession
    ):
        user_update = await UserDAO.update(
            session,
            and_(UserModel.id == user_id),
            obj_in=UserUpdate(
                **user.model_dump(),
            )
        )

        if not user_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user_update
    

    @classmethod
    async def delete_user(
        cls,
        user_id: uuid.UUID,
        session: AsyncSession
    ):
        user = await cls.get_user(user_id, session)

        await UserDAO.update(
            session,
            UserModel.id == user.id,
        )