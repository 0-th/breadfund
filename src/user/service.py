from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.user import exceptions
from src.user.models import User
from src.user.security import check_password, hash_password


async def check_user_exists_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    query_scalars = await db.scalars(select(User).where(User.id == user_id))
    return query_scalars.one_or_none()


async def check_user_exists_by_email(db: AsyncSession, email: str) -> User | None:
    query_scalars = await db.scalars(select(User).where(User.email == email))
    return query_scalars.one_or_none()


async def create_user(
    db: AsyncSession, email: str, first_name: str, last_name: str, password: str
):
    user = User(
        id=uuid4(),
        email=email,
        firstname=first_name,
        lastname=last_name,
        password=hash_password(password),
    )
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    if not (user := await check_user_exists_by_email(db, email)):
        raise exceptions.UserNotFound()
    if not check_password(password, db_password_hash=user.password):
        raise exceptions.InvalidCredentials()
    return user
