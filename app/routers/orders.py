from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_functions.db_order import create_order_in_db, get_order_in_db, patch_order_in_db, \
    get_orders_by_user_id_in_db
from app.functions.auth_functions import get_current_user
from app.schemas import CreateOrder, UpdateOrder
import uuid
from worker.celery_app import celery_app
from worker.tasks import process_order


router = APIRouter(prefix='/orders', tags=['orders'])


@router.post('/create_new_order', status_code=status.HTTP_201_CREATED)
async def create_order(db: Annotated[AsyncSession, Depends(get_db)],
                       create_user: CreateOrder,
                       user: Annotated[dict, Depends(get_current_user)]):
    order_id = str(uuid.uuid4())
    await create_order_in_db(db, create_user, user.get('user_id'), order_id)
    process_order.apply_async(
        args=[order_id],
        queue='new_orders',
        routing_key='new_order'
    )
    return {'status_code':status.HTTP_201_CREATED,
            'transaction': 'Order created successfully'}


@router.get('/{order_id}')
async def get_order(db: Annotated[AsyncSession, Depends(get_db)],
                    order_id: str):
    answer = await get_order_in_db(db, order_id)
    return answer


@router.patch('/update')
async def patch_order(db: Annotated[AsyncSession, Depends(get_db)],
                     order: UpdateOrder):
    await patch_order_in_db(db, order.order_id, order.new_status)
    return {'status_code':status.HTTP_200_OK,
            'transaction': 'Order patched successfully'}


@router.get('/user/{user_id}')
async def get_orders_by_user_id(db: Annotated[AsyncSession, Depends(get_db)],
                                user_id: int):
    answer = await get_orders_by_user_id_in_db(db, user_id)
    return answer