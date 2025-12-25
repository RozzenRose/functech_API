# worker/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import settings

# Синхронный движок для Celery
sync_engine = create_engine(
    settings.database_url_sync,  # postgresql://...
    echo=True
)

SyncSessionLocal = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False
)

def get_sync_db() -> Session:
    """Синхронная сессия для Celery задач"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()