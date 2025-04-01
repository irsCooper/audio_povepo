import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent.parent.parent

load_dotenv()

class YandexInfo(BaseModel):
    client_id: str = os.environ.get('YANDEX_CLIENT_ID')
    client_secret: str = os.environ.get('YANDEX_CLIENT_SECRET')
    redirect_url: str = os.environ.get('YANDEX_REDIRECT_URL')
    token_url: str = os.environ.get('TOKEN_URL')

class Settings(BaseSettings):
    echo: bool = True 
    yandex: YandexInfo = YandexInfo()


settings = Settings()