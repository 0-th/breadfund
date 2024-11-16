from datetime import datetime
from typing import Annotated

from fastapi import File, Form, UploadFile
from pydantic import UUID4, Field
from pydantic.networks import HttpUrl

from src.schemas import CustomModel


class CampaignResponse(CustomModel):
    id: UUID4
    title: str
    description: str
    image: bytes
    goal: int
    amt_reached: int
    percent_reached: float = Field(le=100.0)
    category: list[str]
    no_of_reactions: int
    no_of_donors: int
    deadline: datetime | None


class FeedResponse(CustomModel):
    id: UUID4
    text: str
    media: list[bytes] | None
    no_of_reactions: int


class RetrieveCampaignResponse(CampaignResponse):
    story: str
    social_media_links: list[str]
    feed_posts: list[FeedResponse]
    beneficiary_user_first_name: str | None = None
    beneficiary_user_last_name: str | None = None
    beneficiary_user_email: str | None = None


class CreateCampaignRequest(CustomModel):
    title: Annotated[str, Form()]
    header_img: Annotated[UploadFile, File()]
    description: Annotated[str, Form()]
    story: Annotated[str, Form()]
    goal: Annotated[int, Form()]
    deadline: Annotated[datetime, Form()]
    category: Annotated[list[str], Form()]
    social_media_links: Annotated[list[str], Form()]


class UpdateCampaignRequest(CustomModel):
    title: Annotated[str | None, Form()] = None
    header_img: Annotated[UploadFile | None, File()] = None
    description: Annotated[str | None, Form()] = None
    story: Annotated[str | None, Form()] = None
    goal: Annotated[int | None, Form()] = None
    deadline: Annotated[datetime | None, Form()] = None
    category: Annotated[list[str] | None, Form()] = None
    social_media_links: Annotated[list[str] | None, Form()] = None


class CreateFeedPostRequest(CustomModel):
    text: Annotated[str, Form()]
    media: Annotated[list[UploadFile] | None, Form()] = None


class UpdateFeedPostRequest(CustomModel):
    text: Annotated[str | None, Form()] = None
    media: Annotated[list[UploadFile] | None, Form()] = None


class GenerateCampaignQRCodeRequest(CustomModel):
    full_url_to_campaign_page: HttpUrl
