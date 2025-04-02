from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession


from src.authentication.schemas import TokenInfo
from src.core.config import settings
from src.core.db_helper import db
from src.authentication.service import AuthService
from src.dependencies import get_current_role, http_bearer, get_current_auth_access, get_current_auth_refresh

router = APIRouter(
    prefix="/Authentication", 
    tags=["Authentication"],
    dependencies=[Depends(http_bearer)]
)



@router.get("/PreSignIn")
async def get_yandex_authorise_url():
    """
    Для авторизации через Яндекс необходимо перейти по этой ссылке и подтвердить действие.\n
    Вас перенаправит на по адресу http://localhost:8080/SignIn (то есть, будетвызван метод авторизации).\n 
    На странице вы увидите ответ от сервера, если всё прошло успешно 
    TODO 
    """
    return f"https://oauth.yandex.ru/authorize?response_type=code&client_id={settings.yandex.client_id}"


@router.get("/SignIn", response_model=TokenInfo)
async def sign_in(
    code: str = Query(..., description="Authorization code from Yandex"),
    # cid: str = Query(..., description="Client ID (from query parameters)"),
    session: AsyncSession = Depends(db.session_dependency)
):
    """
    Для получения необходимых данных выполните метод '/Authentication/PreSignIn'
    """
    return await AuthService.sign_in(code, session)


@router.post("/Refresh", status_code=status.HTTP_200_OK, response_model=TokenInfo)
async def refresh_token(
    refresh_token: str,
    session: AsyncSession = Depends(db.session_dependency)
):
    return await AuthService.refresh_tokens(refresh_token, session)
















# @router.get("/YandexUserInfo")
# def get_yandex_user_info(access_token: str = Query(...)):
#     """ Получение данных пользователя по access_token """
#     headers = {"Authorization": f"bearer {access_token}"}

#     response = requests.get(settings.yandex.yandex_info_url, headers=headers)

#     if response.status_code == 200:
#         return response.json()
#     return {"error": "Failed to fetch user info", "details": response.json()}