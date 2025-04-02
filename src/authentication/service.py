from datetime import datetime, timedelta
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
from src.authentication.schemas import RefreshCreate, TokenInfo
from src.authentication.utils import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, decode_jwt
from src.dependencies import create_token_of_type, get_current_auth_user_of_type_token, validate_token_type
from src.exceptions.AuthExceptions import InvalidCredentialsException
from src.accounts.schemas import ROLE_USER, UserCreate
from src.core.config import settings


class AuthService:
    @classmethod
    async def get_auth_tokens_by_yandex(cls, code: str):
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
        

    @classmethod
    async def get_user_info_by_yandex(cls, access_token: str):
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
        
        await RefreshTokenDAO.add(
            session,
            RefreshCreate(
                reftesh_token=refresh_token,
                expire_in=int((datetime.utcnow() + timedelta(days=settings.auth_jwt.refresh_token_expire_days)).timestamp()),
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
    ): 
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
                user = await cls.sign_up(user_info, session)

            # TODO
        except:
            raise



    @classmethod
    async def validate_access_token(cls, access_token: str):
        try: 
            return await decode_jwt(access_token)
        except Exception as e:
            print(e)
            return None
        
    
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

    