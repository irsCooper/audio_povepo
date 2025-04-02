from src.audio.model import AudioModel
from src.audio.schemas import AudioCreate, AudioUpdate
from src.base_dao import BaseDAO


class AudioDAO(BaseDAO[AudioModel, AudioCreate, AudioUpdate]):
    model = AudioModel