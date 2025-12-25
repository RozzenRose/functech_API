# worker/tasks.py
import time

from celery import Celery
from app.database.models import Order  # ТА ЖЕ САМАЯ модель!
from worker.database import sync_engine, get_sync_db
from sqlalchemy.orm import Session
from config import settings
from sqlalchemy import select, update
from app.database.models.orders import OrderStatus
import json
from redis_inf import Redis


celery_app = Celery(__name__, broker=settings.rabbitmq_url)


def update_order_from_worker(order_id, new_status):
    redis = Redis.get_sync_redis()
    pattern = f'orders:{order_id}'
    current_data = redis.get(pattern)
    if not current_data:
        return None
    order = json.loads(current_data)
    order['status'] = new_status
    updated_data = json.dumps(order)
    redis.set(pattern, updated_data, ex=60 * 5)


def patch_order_in_db(db, order_id: int) -> None:
    querry = (
        select(Order.status)
        .where(Order.id == order_id)
        .with_for_update()  # Блокируем записи до коммита
    )
    try:
        result = db.execute(querry)
    except:
        db.rollback()

    old_status = result.scalar_one()  # Получаем объект
    print(old_status)
    if old_status == OrderStatus.SHIPPED:
        new_status = OrderStatus.CANCELED
    if old_status == OrderStatus.PAID:
        new_status = OrderStatus.SHIPPED
    if old_status == OrderStatus.PENDING:
        new_status = OrderStatus.PAID

    db.execute(
        update(Order)
        .where(Order.id == order_id)
        .values(status=new_status)
    )
    db.commit()  # Блокировка снимается при коммите
    update_order_from_worker(order_id, new_status)
    if new_status == OrderStatus.CANCELED:
        return True


@celery_app.task
def process_order(order_id: str):
    while True:
        print('работает')
        time.sleep(60)

        for db in get_sync_db():
            if patch_order_in_db(db, order_id):
                return
