from app.database.models import User, RefreshTokenList
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert


async def add_refresh_token_in_db(db, user_id: int, token: str) -> None:
    data = insert(RefreshTokenList).values(
        owner_id=user_id,
        refresh_token=token).on_conflict_do_nothing()
    await db.execute(data)
    await db.commit()


async def update_refresh_token_in_db(db, id, refresh_token) -> None:
    query = update(RefreshTokenList).where(RefreshTokenList.owner_id == id).values(refresh_token=refresh_token)
    await db.execute(query)
    await db.commit()
