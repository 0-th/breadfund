from datetime import datetime
from typing import Any, AsyncGenerator
from uuid import UUID, uuid4

from sqlalchemy import MetaData, NullPool, func, make_url
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

DATABASE_URL = str(settings.DATABASE_URL)

url = make_url(DATABASE_URL)
url = url.set(query={"ssl": "require"})

engine = create_async_engine(
    url=url,
    echo=settings.ENVIRONMENT.is_debug,
    pool_pre_ping=True,
    poolclass=NullPool if settings.ENVIRONMENT.is_testing else None,
)

async_session = async_sessionmaker(bind=engine)

metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


async def session() -> AsyncGenerator[AsyncSession, Any]:
    # session-scoped request is handled by ctx-mgr
    # begin-rollback (if exception occurs) -->> commit (if no exception) -->> close
    async with async_session.begin() as async_db_session:
        yield async_db_session


class CommonFieldsMixin:
    """
    Define a series of common fields that may be applied to mapped classes using this
    class as mixin class
    """

    id: Mapped[UUID] = mapped_column(primary_key=True, insert_default=uuid4, init=False)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=None, server_default=func.now(), init=False
    )
    update_at: Mapped[datetime | None] = mapped_column(
        default=None, onupdate=func.now(), init=False
    )


class Base(MappedAsDataclass, AsyncAttrs, DeclarativeBase):
    metadata = metadata
    # type_annotation_map = {
    #     bytes: LargeBinary()
    # }
    # keeping it to remind myself that it's available

    # default type_annotation_map can be found in the sqlalchemy doc below
    # https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-annotated-declarative-table-type-annotated-forms-for-mapped-column
