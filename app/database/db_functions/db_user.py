from app.database.models import User
from app.schemas import CreateUser
from sqlalchemy import insert, select, update


async def create_user_in_db(db, user_data: CreateUser, hashed_password: str) -> None:
    data = insert(User).values(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password)
    await db.execute(data)
    await db.commit()


async def get_user(db, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalars().first()
    return user


async def disactivate_user_in_db(db, user_id):
    query = update(User).where(User.id == user_id).values(is_activate=False)
    await db.execute(query)
    await db.commit()
