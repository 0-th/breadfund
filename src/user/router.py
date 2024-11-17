from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette import status

from src.database import session
from src.user import dependencies as deps
from src.user import schemas, service

user_router = APIRouter()


@user_router.post(
    "/signup",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data: Annotated[schemas.UserCreateRequest, Depends(deps.validate_user_not_exist)],
    db: Annotated[AsyncSession, Depends(session)],
) -> None:
    await service.create_user(
        db, data.email, data.first_name, data.last_name, data.password, data.gender
    )
    return


@user_router.post(
    "/login",
    response_model=schemas.LoginUserResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(session)],
) -> schemas.LoginUserResponse:
    user = await service.authenticate_user(db, data.username, data.password)
    return schemas.LoginUserResponse(access_token=deps.generate_access_token(user))
