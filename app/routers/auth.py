from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import CreateUser
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.functions.hashing import pass_hasher, pass_verify
from app.functions.auth_functions import (create_access_token, get_current_user,
                                          create_refresh_token, verify_refresh_token)
from datetime import timedelta
from app.database.db_functions import (add_refresh_token_in_db,
                                       disactivate_user_in_db, create_user_in_db, get_user,
                                        update_refresh_token_in_db)
from app.redis_inf import Redis


router = APIRouter(prefix='/auth', tags=['auth'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


@router.get("/me")
async def read_users_me(token: Annotated[str, Depends(oauth2_scheme)]):
    '''Возвращает данные о залогиненном юзере'''
    user = await get_current_user(token) # Запрос в БД
    return {"user_id": user.get('user_id'),
            "username": user.get('username'),
            "email": user.get('email'),}


@router.post('/create_user', status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser):
    '''Создаем пользователей'''
    hashed_password = await pass_hasher(create_user.password) # Хешируем пароль
    await create_user_in_db(db, create_user, hashed_password) # Сохраняем данные в БД
    return {'status_code':status.HTTP_201_CREATED,
            'transaction': 'User created successfully'}


@router.post('/token')
async def login(db: Annotated[AsyncSession, Depends(get_db)],
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    '''Логиним пользователя'''
    user = await get_user(db, form_data.username) # Достаем его данные из БД
    if not user: # Проверяем, что пользователь существует
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User is not exist')
    if not await pass_verify(user.hashed_password, form_data.password): # Сверяем хеш паролей
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid password')
    token = await create_access_token(user.id, user.username, # Генерируем токен доступа
                                      user.email,
                                      expires_delta=timedelta(minutes=20))
    refresh_token = await create_refresh_token(user.id, user.username) # Генерируем токен обновления
    await add_refresh_token_in_db(db, user.id, refresh_token) # Сохраняем токен обновления
    return {'access_token': token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'}


@router.post('/refresh')
async def refresh_tokens(db: Annotated[AsyncSession, Depends(get_db)],
                        refresh_token: str):
    '''Обновляем токены, если access закончился'''
    id, username = await verify_refresh_token(refresh_token) # Проверяем refresh
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid refresh token')
    user = await get_user(db, username) # Достаем данные пользователя из БД
    #await delete_refresh_token_in_db(db, id) # Удаляем старый refresh
    access_token = await create_access_token(user.id, user.username, # Генерируем новый access
                                             user.email,
                                             expires_delta=timedelta(minutes=20))
    new_refresh_token = await create_refresh_token(user.id, user.username) # Генерируем новый refresh
    await update_refresh_token_in_db(db, user.id, new_refresh_token) # Сохраняем новый refresh
    return {'access_token': access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'bearer'}
