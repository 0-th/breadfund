from pydantic import UUID4, Field
from pydantic.networks import HttpUrl
from pydantic.types import NaiveDatetime

from src.schemas import CustomModel


class CampaignResponse(CustomModel):
    id: UUID4
    title: str
    description: str
    image: str
    goal: int
    amt_reached: int
    percent_reached: float = Field(le=100.0)
    category: list[str]
    no_of_reactions: int
    no_of_donors: int
    deadline: NaiveDatetime | None


class FeedResponse(CustomModel):
    id: UUID4
    text: str
    media: list[str] | None
    no_of_reactions: int


class RetrieveCampaignResponse(CampaignResponse):
    story: str
    social_media_links: list[str]
    feed_posts: list[FeedResponse]
    beneficiary_user_first_name: str | None = None
    beneficiary_user_last_name: str | None = None
    beneficiary_user_email: str | None = None


class GenerateCampaignQRCodeRequest(CustomModel):
    full_url_to_campaign_page: HttpUrl


class SaveDonationRequest(CustomModel):
    payaza_reference: str
    transaction_reference: str
    amount_received: float
    name: str
    social_media_links: list[str] | None
    anonymous: bool
    recovery_acct_no: int
    recovery_acct_bank: str
    recovery_acct_name: str


class DonationResponse(CustomModel):
    id: UUID4
    anonymous: bool
    name: str | None
    social_media_link: list[str] | None
    amount: float
