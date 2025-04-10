from datetime import datetime
import uuid
from fastapi.security import HTTPAuthorizationCredentials
import jwt

from src.core.config import settings


TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


async def encode_jwt(
        payload: dict,
        keys: str = settings.auth_jwt.private_key_path.read_text(),
        algorithms: str = settings.auth_jwt.algorithms,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes
):
    to_encode = payload.copy()
    now = datetime.now()
    
    to_encode.update(
        exp=now + expire_minutes,
        iat=now,
        jti=str(uuid.uuid4())
    )

    encoded = jwt.encode(
        payload=to_encode,
        key=keys,
        algorithm=algorithms
    )
    return encoded


async def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithms: str = settings.auth_jwt.algorithms
):
    if isinstance(token, HTTPAuthorizationCredentials):
        token = token.credentials

    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=algorithms
    )
    return decoded