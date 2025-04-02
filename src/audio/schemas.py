import uuid
from pydantic import BaseModel, ConfigDict


class Audio(BaseModel):
    filename: str
    file_path: str


class AudioSchema(Audio):
    model_config = ConfigDict(from_attributes=True)


class AudioCreate(Audio):
    user_id: uuid.UUID


class AudioUpdate(BaseModel):
    pass
