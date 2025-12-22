from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings
from fastapi import Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


async def create_access_token(user_id: int, username: str, email: str, expires_delta: timedelta):
    '''Создаем access'''
    payload = {'user_id': user_id,
               'username': username,
               'email': email,
               'exp': datetime.now(timezone.utc) + expires_delta}
    payload['exp'] = int(payload['exp'].timestamp())
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


async def create_refresh_token(user_id, username: str) -> str:
    payload = {'id': user_id, 'username': username}
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    '''Дешефруем access'''
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm]) #Декодирование токена
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token')
    user_id: int | None = payload.get('user_id')
    username: str | None = payload.get('username')
    email: str | None = payload.get('email')
    expire: int | None = payload.get('exp')

    current_time = datetime.now(timezone.utc).timestamp()

    return {'user_id': user_id,
            'username': username,
            'email': email,
            'expire': expire > current_time,
            'token': token}


async def verify_refresh_token(token: str) -> str | None:
    '''Дешефруем refresh'''
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    return payload.get('id'), payload.get('username')
