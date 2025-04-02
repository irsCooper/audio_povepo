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
    yandex_info_url: str = os.environ.get('YANDEX_INFO_URL')


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certificates" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certificates" / "jwt-publick.pem"
    algorithms: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30 


class Settings(BaseSettings):
    echo: bool = True 
    auth_jwt: AuthJWT = AuthJWT()
    yandex: YandexInfo = YandexInfo()
    db_url: str = os.environ.get('DB_URL')
    audio_path: Path = BASE_DIR / "audio"


settings = Settings()