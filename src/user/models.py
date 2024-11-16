from enum import Enum
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Gender(str, Enum):
    male = "male"
    female = "female"


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    gender: Mapped[Gender] = mapped_column(String(255))
    firstname: Mapped[str] = mapped_column(String(255))
    lastname: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
