from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict


ROLE_USER = "User"
ROLE_ADMIN = "Admin"


class RoleSchema(BaseModel):
    name_role: str


class UserDB(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    display_name: str
    real_name: str
    first_name: str
    last_name: str
    default_email: str
    birthday: str
    psuid: str
    roles: list["RoleSchema"]

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    client_id: uuid.UUID
    display_name: str
    real_name: str
    first_name: str
    last_name: str
    default_email: str
    birthday: str
    psuid: str
    roles: Optional[List[str]] = None


class UserUpdate(BaseModel):
    id: uuid.UUID
    display_name: str
    real_name: str
    first_name: str
    last_name: str
    birthday: str
