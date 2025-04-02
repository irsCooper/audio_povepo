from datetime import datetime
from typing import Optional
import uuid
from fastapi import HTTPException
import requests
from sqlalchemy.ext.asyncio import AsyncSession

from src.authentication.model import RefreshModel
from src.authentication.dao import RefreshTokenDAO
from src.accounts.dao import UserDAO
from src.accounts.model import UserModel
from src.accounts.service import UserService
from src.authentication.schemas import RefreshCreate, RefreshUpdate, TokenInfo
from src.authentication.utils import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from src.dependencies import create_token_of_type, get_current_auth_user_of_type_token
from src.exceptions.AuthExceptions import InvalidCredentialsException
from src.accounts.schemas import ROLE_USER, UserCreate
from src.core.config import settings


class AuthService:
    @staticmethod
    async def get_auth_tokens_by_yandex(code: str):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.yandex.client_id, 
            "client_secret": settings.yandex.client_secret,
            "response_type": 'token',
            "redirect_uri": settings.yandex.redirect_url
        }

        response = requests.post(settings.yandex.token_url, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
        

    @staticmethod
    async def get_user_info_by_yandex(access_token: str):
        response = requests.get(
            settings.yandex.yandex_info_url, 
            headers={"Authorization": f"bearer {access_token}"}
        )

        if response.status_code == 200:
            return response.json()
        
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )


    @classmethod
    async def create_token(cls, user: UserModel, session: AsyncSession) -> TokenInfo:
        access_token = await create_token_of_type(ACCESS_TOKEN_TYPE, user)

        refresh_id = uuid.uuid4()
        refresh_token = await create_token_of_type(REFRESH_TOKEN_TYPE, user, refresh_id)
        
        refresh_model: RefreshModel = await RefreshTokenDAO.find_one_or_none(
            session,
            RefreshModel.user_id == user.id
        )

        if not refresh_model:
            await RefreshTokenDAO.add(
                session,
                RefreshCreate(
                    id=refresh_id,
                    refresh_token=refresh_token,
                    expire_in=settings.auth_jwt.refresh_token_expire_days * 24 * 60,
                    user_id=user.id
                )
            )
        else:
            await RefreshTokenDAO.update(
                session,
                RefreshModel.user_id == user.id,
                obj_in=RefreshUpdate(
                    id=refresh_model.id,
                    refresh_token=refresh_token,
                    creates_at=datetime.now(),
                )
            )

        await session.commit()

        return TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token
        )

    
    @classmethod
    async def sign_up(
        cls, 
        user_info: dict, 
        session: AsyncSession
    ) -> Optional[UserModel]: 
        return await UserService.create_user(
            user_in=UserCreate(
                login=user_info["login"],
                display_name=user_info["display_name"],
                real_name=user_info["real_name"],
                first_name=user_info["first_name"],
                last_name=user_info["last_name"],
                default_email=user_info["default_email"],
                birthday=user_info["birthday"],
                psuid=user_info["psuid"],
                roles=[ROLE_USER]
            ),
            session=session
        )


    @classmethod
    async def sign_in(
        cls,
        code: str,
        session: AsyncSession,
    ):
        try: 
            yandex_auth_tokens: dict = await cls.get_auth_tokens_by_yandex(code)
            user_info: dict = await cls.get_user_info_by_yandex(yandex_auth_tokens["access_token"])

            user: UserModel = await UserDAO.find_one_or_none(
                session,
                UserModel.login == user_info["login"]
            )

            if not user:
                user: UserModel = await cls.sign_up(user_info, session)

            if user:
                return await cls.create_token(user, session)
            
            raise InvalidCredentialsException
        except Exception as e:
            raise e
        
    
    @classmethod
    async def refresh_tokens(
        cls,
        refresh_token: str,
        session: AsyncSession
    ):
        user = await get_current_auth_user_of_type_token(
            token=refresh_token, 
            token_type=REFRESH_TOKEN_TYPE, 
            session=session
        )

        return await cls.create_token(
            user=user,
            session=session
        )

    