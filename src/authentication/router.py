from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession


from src.accounts.model import UserModel
from src.authentication.schemas import TokenInfo
from src.core.config import settings
from src.core.db_helper import db
from src.authentication.service import AuthService
from src.dependencies import http_bearer, get_current_auth_access


router = APIRouter(
    prefix="/Authentication", 
    tags=["Authentication"],
)


@router.get("/PreSignIn")
async def get_yandex_authorise_url():
    """
    Для авторизации через Яндекс необходимо перейти по ссылке, которую вы увидите при вызове метода и подтвердить действие на открывшейся странице.\n
    Даллее вас перенаправит на по адресу http://localhost:8080/SignIn (то есть, будет вызван метод авторизации в нашей системе).\n 
    На открывшейся странице вы увидите ответ от сервера, не спешите закрывать страницу.\n 
    Читайте инструкцию по взаимдействию в файле README.md в корне проекта
    """
    return f"https://oauth.yandex.ru/authorize?response_type=code&client_id={settings.yandex.client_id}"


@router.get("/SignIn", response_model=TokenInfo)
async def sign_in(
    code: str = Query(..., description="Authorization code from Yandex"),
    session: AsyncSession = Depends(db.session_dependency)
):
    """
    Для получения необходимых данных выполните метод '/Authentication/PreSignIn'
    """
    return await AuthService.sign_in(code, session)


@router.post("/Refresh", status_code=status.HTTP_200_OK, response_model=TokenInfo)
async def refresh_token(
    refresh_token: str,
    user: UserModel = Depends(get_current_auth_access),
    session: AsyncSession = Depends(db.session_dependency)
):
    """
    Обновление access и refresh токенов
    """
    return await AuthService.refresh_tokens(refresh_token, session)
















# @router.get("/YandexUserInfo")
# def get_yandex_user_info(access_token: str = Query(...)):
#     """ Получение данных пользователя по access_token """
#     headers = {"Authorization": f"bearer {access_token}"}

#     response = requests.get(settings.yandex.yandex_info_url, headers=headers)

#     if response.status_code == 200:
#         return response.json()
#     return {"error": "Failed to fetch user info", "details": response.json()}