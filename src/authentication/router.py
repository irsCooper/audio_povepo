from fastapi import APIRouter, Query
import requests

from src.core.config import settings

router = APIRouter(
    prefix="/Authentication", 
    tags=["Authentication"],
)



@router.get("/PreSignIn")
def get_yandex_authorise_url():
    """
    Для авторизации через Яндекс необходимо перейти по этой ссылке и подтвердить действие.\n
    Вас перенаправит на по адресу http://localhost:8080/SignIn (то есть, будетвызван метод авторизации).\n 
    На странице вы увидите ответ от сервера, если всё прошло успешно 
    TODO 
    """
    return f"https://oauth.yandex.ru/authorize?response_type=code&client_id={settings.yandex.client_id}"


@router.get("/SignIn")
def sign_in(
    code: str = Query(..., description="Authorization code from Yandex"),
    cid: str = Query(..., description="Client ID (from query parameters)")
):
    """
    Для получения необходимых данных выполните метод '/Authentication/PreSignIn'
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.yandex.client_id, 
        "client_secret": settings.yandex.client_secret,
        "response_type": 'token',
        "redirect_uri": settings.yandex.redirect_url
    }

    response = requests.post(settings.yandex.token_url, data=data)

    if response.status_code == 200:
        tokens_info = response.json()

        
    
    return {"error": "Failed to get access token", "details": response.json()}

@router.get("/YandexUserInfo")
def get_yandex_user_info(access_token: str = Query(...)):
    """ Получение данных пользователя по access_token """
    headers = {"Authorization": f"bearer {access_token}"}

    response = requests.get(settings.yandex.yandex_info_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch user info", "details": response.json()}