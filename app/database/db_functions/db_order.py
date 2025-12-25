from app.database.models import User, Order
from app.schemas import CreateOrder
from sqlalchemy import insert, select, update
from worker.tasks import process_order
from redis_inf import Redis, OrderChach
import json


async def create_order_in_db(db, order_data: CreateOrder, user_id: int, order_id: str) -> None:
    data = insert(Order).values(
        id=order_id,
        user_id=user_id,
        items=order_data.items,
        total_price=order_data.total_price)
    await db.execute(data)
    await db.commit()


async def get_order_in_db(db, order_id: int) -> Order | None:
    redis = await Redis.get_redis()
    order_chach = OrderChach(redis)
    order = await order_chach.get_orders_with_order_id(order_id)
    if order:
        return order
    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalars().first()
    await order_chach.save_order(order)
    return order


async def patch_order_in_db(db, order_id: int, new_status: str) -> None:
    redis = await Redis.get_redis()
    order_chach = OrderChach(redis)
    await order_chach.update_order_with_order_id(order_id, new_status)
    await db.execute(
        update(Order)
        .where(Order.id == order_id)
        .values(status=new_status)
    )
    await  db.commit()


async def get_orders_by_user_id_in_db(db, user_id: int) -> list[Order]:
    redis = await Redis.get_redis()
    order_chach = OrderChach(redis)
    orders = await order_chach.get_orders_with_user_id(user_id)
    if orders:
        return orders
    query = select(Order).where(Order.user_id == user_id)
    result = await db.execute(query)
    orders = result.scalars().all()
    await order_chach.save_order_with_user_id(user_id, orders)
    return orders
