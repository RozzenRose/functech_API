# worker/celery_app.py
from celery import Celery
from config import settings

# Создаем Celery app с RabbitMQ как брокер
celery_app = Celery(
    'order_worker',
    broker=settings.rabbitmq_url,  # RabbitMQ URL
    backend=settings.redis_url,  # Redis для результатов
    include=['worker.tasks']  # Где искать задачи
)

# Конфигурация
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,

    # Настройки воркера
    worker_prefetch_multiplier=1,  # По одной задаче за раз
    task_acks_late=True,  # Подтверждать после выполнения
    task_reject_on_worker_lost=True,

    # Очереди
    task_default_queue='new_orders',
    task_queues={
        'new_orders': {

            'exchange': 'new_orders',
            'routing_key': 'new_order'
        }
    }
)
