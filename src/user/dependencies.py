from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.config import settings
from src.database import session
from src.user import exceptions, service
from src.user.exceptions import InvalidAccessToken
from src.user.models import User
from src.user.schemas import AccessTokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="", scopes={})


def parse_access_token(
    access_token: Annotated[str, Depends(oauth2_scheme)],
) -> AccessTokenData:
    try:
        payload = jwt.decode(
            access_token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALG]
        )
        token_payload_valid = AccessTokenData(**payload)
    except (JWTError, ValidationError):
        raise InvalidAccessToken()

    return token_payload_valid


async def validate_user_access_token(
    db: Annotated[AsyncSession, Depends(session)],
    token_data: Annotated[AccessTokenData, Depends(parse_access_token)],
) -> User:
    user = await service.check_user_exists_by_id(db, user_id=token_data.sub)
    if not user:
        raise exceptions.InvalidAccessToken()

    return user
