import redis as sync_redis
import redis.asyncio as redis
from config import settings
from app.schemas import CreateOrder
import json


class Redis:
    _redis = None
    _sync_redis = None

    @classmethod
    async def get_redis(cls):
        if cls._redis is None:
            cls._redis = redis.from_url(settings.redis_url, decode_responses=True)
        return cls._redis

    @classmethod
    def get_sync_redis(cls):
        if cls._sync_redis is None:
            cls._sync_redis = sync_redis.from_url(settings.redis_url, decode_responses=True)
        return cls._sync_redis


class OrderChach:
    def __init__(self, redis):
        self.redis = redis


    async def save_order(self, order):
        order = order.to_dict()
        await self.redis.unlink(f'user:{order["user_id"]}:orders')
        async with self.redis.pipeline(transaction=True) as pipe:
            pattern = f'orders:{order["id"]}'
            data = json.dumps(order)
            await pipe.set(pattern, data)
            await pipe.expire(pattern, 60*5) # 5 минут
            await pipe.execute()


    async def update_order_with_order_id(self, order_id, new_status):
        pattern = f'orders:{order_id}'
        current_data = await self.redis.get(pattern)
        if not current_data:
            return None
        order = json.loads(current_data)
        order['status'] = new_status
        updated_data = json.dumps(order)
        await self.redis.set(pattern, updated_data, ex=60*5)


    async def get_orders_with_order_id(self, order_id):
        pattern = f'orders:{order_id}'
        answer = await self.redis.get(pattern)
        if not answer:
            return None
        return json.loads(answer)


    async def save_order_with_user_id(self, user_id, orders):
        async with self.redis.pipeline(transaction=True) as pipe:
            pattern = f'user:{user_id}:orders'
            await pipe.set(pattern, json.dumps([item.to_dict() for item in orders]))
            await pipe.expire(pattern, 60 * 5)  # 5 минут
            await pipe.execute()


    async def get_orders_with_user_id(self, user_id):
        pattern = f'user:{user_id}:orders'
        answer = await self.redis.get(pattern)
        if not answer:
            return None
        return json.loads(answer)