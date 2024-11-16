import re
from datetime import datetime
from typing import Annotated, TypeAlias

from pydantic import UUID4, HttpUrl
from pydantic.fields import Field
from pydantic.functional_validators import field_validator
from pydantic.networks import EmailStr
from pydantic.types import StringConstraints

from src.schemas import CustomModel
from src.user.models import Gender

STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


class AccessTokenData(CustomModel):
    iss: HttpUrl
    iat: datetime
    exp: datetime
    nbf: datetime
    jti: str
    sub: UUID4
    prv: str


Password: TypeAlias = Annotated[
    str,
    Field(
        min_length=6,
        max_length=128,
        examples=["Password@1"],
        description=(
            "Password must contain at least one lower character, "
            "one upper character, digit or special symbol"
        ),
    ),
]


def validate_password(password: str) -> str:
    if not STRONG_PASSWORD_PATTERN.match(password):
        raise ValueError(
            "password must contain at least "
            "one lower character, "
            "one upper character, "
            "digit or "
            "special symbol"
        )
    return password


class UserSchemaCommon(CustomModel):
    email: Annotated[EmailStr, StringConstraints(to_lower=True)]
    gender: Gender
    first_name: str
    last_name: str


class UserCreateRequest(UserSchemaCommon):
    password: Password

    _validate_password = field_validator("password", mode="after")(validate_password)


class LoginUserRequest(CustomModel):
    email: EmailStr
    password: str
