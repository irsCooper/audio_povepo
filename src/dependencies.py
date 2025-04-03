from datetime import datetime, timedelta
from typing import Optional
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

import jwt

from src.accounts.service import UserService
from src.accounts.model import UserModel
from src.authentication.utils import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, TOKEN_TYPE_FIELD, decode_jwt, encode_jwt
from src.core.config import settings
from src.core.db_helper import db


http_bearer = HTTPBearer(auto_error=False)


async def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int 
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)

    return await encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes
    )


async def create_token_of_type(
    token_type: str, 
    user: UserModel,
    refresh_id: Optional[uuid.UUID] = None
) -> str:
    
    jwt_payload = {
        "sub": str(user.id),
    }

    if token_type == ACCESS_TOKEN_TYPE:
        jwt_payload.update({
            "login": user.login,
            "display_name": user.display_name,
            "default_email": user.default_email,
            "roles": [role.name_role for role in user.roles],
        })

        expire_minutes: int = timedelta(minutes=settings.auth_jwt.access_token_expire_minutes)
        
    else:
        jwt_payload.update({
            "id": str(refresh_id), 
        })

        expire_minutes: int = timedelta(days=settings.auth_jwt.refresh_token_expire_days)

    return await create_jwt(
        token_type=token_type,
        token_data=jwt_payload,
        expire_minutes=expire_minutes
    )


async def validate_token_type(
    payload: dict, 
    token_type: str
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True 
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invalid token type {current_token_type!r} expected {token_type!r}"
    )


async def get_user_by_token_sub(
    payload: dict, 
    session: AsyncSession
) -> Optional[UserModel]:
    user_id = payload.get("sub")
    user: UserModel = await UserService.get_user(user_id=user_id, session=session) 
    if user:
        return user 
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid token"
    )


async def get_current_auth_user_of_type_token(
    token: str | bytes,
    token_type: str,
    session: AsyncSession
):
    try:
        payload: dict = await decode_jwt(token)
        
        if payload["exp"] - int(datetime.now().timestamp()) < 0:
            raise 

        await validate_token_type(
            payload=payload,
            token_type=token_type
        )
        return await get_user_by_token_sub(
            payload=payload,
            session=session
        )
        
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Not authenticated"
        )



def get_current_auth_user(token_type: str) -> Optional[UserModel]:
    async def get_auth_user_from_token(
        token: str | bytes = Depends(http_bearer),
        session: AsyncSession = Depends(db.session_dependency),
    ):
        return await get_current_auth_user_of_type_token(
            token=token, 
            token_type=token_type, 
            session=session
        )
    
    return get_auth_user_from_token


get_current_auth_access = get_current_auth_user(ACCESS_TOKEN_TYPE)
get_current_auth_refresh = get_current_auth_user(REFRESH_TOKEN_TYPE)


async def get_current_role(
    name_role: str,
    user: UserModel
): 
    if any(role.name_role in name_role for role in user.roles):
        return
                
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )          
