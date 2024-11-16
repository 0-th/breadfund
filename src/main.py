from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from src.campaign.router import campaign_router
from src.config import app_configs
from src.user.router import user_router

app = FastAPI(**app_configs)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=(
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ),
)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=str(app.openapi_url),
        title=app.title,
    )


app.include_router(campaign_router, prefix="/campaign", tags=["Campaign"])
app.include_router(user_router, prefix="/user", tags=["User"])
