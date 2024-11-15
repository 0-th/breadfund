from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.user.models import User


async def check_user_exists_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    query_scalars = await db.scalars(select(User).where(User.id == user_id))
    return query_scalars.one_or_none()


async def check_user_exists_by_email(db: AsyncSession, email: str) -> User | None:
    query_scalars = await db.scalars(select(User).where(User.email == email))
    return query_scalars.one_or_none()
