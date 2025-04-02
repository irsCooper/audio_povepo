from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from typing import Any, Dict, Optional, Union

from exceptions import DatabaseException
from exceptions.DatabaseException import UnknowanDatabaseException
from src.authentication.model import RefreshModel, YandexSession
from src.authentication.schemas import RefreshCreate, RefreshUpdate, YandexSessionCreate, YandexSessionUpdate
from src.base_dao import BaseDAO


class RefreshTokenDAO(BaseDAO[RefreshModel, RefreshCreate, RefreshUpdate]):
    model = RefreshModel


class YandexSessionDAO(BaseDAO[YandexSession, YandexSessionCreate, YandexSessionUpdate]):
    model = YandexSession