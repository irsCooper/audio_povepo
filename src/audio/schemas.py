import uuid
from pydantic import BaseModel, ConfigDict


class AudioSchema(BaseModel):
    filename: str
    file_path: str
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class AudioCreate(BaseModel):
    filename: str
    file_path: str
    user_id: uuid.UUID


class AudioUpdate(BaseModel):
    pass
