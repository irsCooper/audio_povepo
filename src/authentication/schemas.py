import uuid
from pydantic import BaseModel
from datetime import datetime


class RefreshCreate(BaseModel):
    id: uuid.UUID
    refresh_token: str 
    expire_in: int 
    user_id: uuid.UUID


class RefreshUpdate(BaseModel):
    id: uuid.UUID
    refresh_token: str
    creates_at: datetime


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class YandexSessionCreate(BaseModel):
    access_token: str
    refresh_token: str
    expire_in: int
    refresh_session_id: uuid.UUID


class YandexSessionUpdate(YandexSessionCreate):
    id: uuid.UUID