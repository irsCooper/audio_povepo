from audio_povepo.src.audio.model import AudioModel
from audio_povepo.src.audio.schemas import AudioCreate, AudioUpdate
from src.base_dao import BaseDAO


class AudioDAO(BaseDAO[AudioModel, AudioCreate, AudioUpdate]):
    model = AudioModel