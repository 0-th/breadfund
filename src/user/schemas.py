from datetime import datetime

from pydantic import UUID4, HttpUrl

from src.schemas import CustomModel


class AccessTokenData(CustomModel):
    iss: HttpUrl
    iat: datetime
    exp: datetime
    nbf: datetime
    jti: str
    sub: UUID4
    prv: str
