from base64 import b64encode
from io import BytesIO
from typing import Annotated
from uuid import UUID

import segno
from fastapi import APIRouter, Depends, Form, Query, Response, UploadFile, status
from pydantic.types import UUID4, NaiveDatetime
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.campaign import dependencies, schemas, service
from src.campaign.constants import CampaignProgress
from src.campaign.models import Campaign, FeedPost
from src.database import session
from src.user import exceptions as user_exceptions
from src.user import service as user_service
from src.user.dependencies import validate_user_access_token
from src.user.models import User

campaign_router = APIRouter()


@campaign_router.get(
    "/hot",
    response_model=list[schemas.CampaignResponse],
    status_code=status.HTTP_200_OK,
)
async def retrieve_popular_campaigns(
    db: Annotated[AsyncSession, Depends(session)],
    limit: Annotated[int, Query(ge=0, le=10)] = 5,
    skip: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.CampaignResponse]:
    campaigns = await service.retrieve_campaigns_with_highest_reactions_and_donors(
        db, limit, skip
    )
    campaigns_response_schemas = []
    for campaign in campaigns:
        amt_reached_in_percent = (
            (campaign.amt_reached / campaign.goal) * 100 if campaign.goal else 0.0
        )
        campaign_response = schemas.CampaignResponse(
            id=campaign.id,
            title=campaign.title,
            description=campaign.description,
            image=b64encode(campaign.header_img).decode(),
            goal=campaign.goal,
            amt_reached=campaign.amt_reached,
            percent_reached=amt_reached_in_percent,
            category=campaign.category,
            no_of_reactions=campaign.no_of_reactions,
            no_of_donors=campaign.no_of_supporters,
            deadline=campaign.deadline,
        )
        campaigns_response_schemas.append(campaign_response)

    return campaigns_response_schemas


@campaign_router.get(
    "/{campaign_id}",
    response_model=schemas.RetrieveCampaignResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(validate_user_access_token)],
    summary="Retrieve campaign information in detail",
)
async def retrieve_campaign(
    db: Annotated[AsyncSession, Depends(session)],
    campaign: Annotated[Campaign, Depends(dependencies.validate_campaign_exist)],
) -> schemas.RetrieveCampaignResponse:
    amt_reached_in_percent = (
        (campaign.amt_reached / campaign.goal) * 100 if campaign.goal else 0.0
    )
    campaign_feed_posts: list[schemas.FeedResponse] = []
    for feed_post in await campaign.awaitable_attrs.feed_posts:
        campaign_feed_posts.append(
            schemas.FeedResponse(
                id=feed_post.id,
                text=feed_post.text,
                media=[
                    b64encode(feed_post_medium_bytes).decode()
                    for feed_post_medium_bytes in feed_post.media
                ]
                if feed_post.media
                else None,
                no_of_reactions=feed_post.no_of_reactions,
            )
        )
    beneficiary_user = None
    if campaign.beneficiary_user_id:
        beneficiary_user = await db.get_one(User, campaign.beneficiary_user_id)
    return schemas.RetrieveCampaignResponse(
        id=campaign.id,
        title=campaign.title,
        description=campaign.description,
        image=b64encode(campaign.header_img).decode(),
        goal=campaign.goal,
        amt_reached=campaign.amt_reached,
        percent_reached=amt_reached_in_percent,
        category=campaign.category,
        no_of_reactions=campaign.no_of_reactions,
        no_of_donors=campaign.no_of_supporters,
        deadline=campaign.deadline,
        story=campaign.story,
        social_media_links=campaign.social_media_links,
        feed_posts=campaign_feed_posts,
        beneficiary_user_first_name=(
            beneficiary_user.firstname if beneficiary_user else None
        ),
        beneficiary_user_last_name=(
            beneficiary_user.lastname if beneficiary_user else None
        ),
        beneficiary_user_email=(beneficiary_user.email if beneficiary_user else None),
    )


@campaign_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UUID4,
    summary="Create a campaign",
)
async def create_campaign(
    db: Annotated[AsyncSession, Depends(session)],
    user: Annotated[User, Depends(validate_user_access_token)],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    story: Annotated[str, Form()],
    goal: Annotated[int, Form()],
    deadline: Annotated[NaiveDatetime, Form()],
    category: Annotated[list[str], Form()],
    social_media_links: Annotated[list[str], Form()],
    header_img: UploadFile,
) -> UUID:
    await header_img.seek(0)
    campaign = await service.create_campaign(
        db,
        title,
        await header_img.read(),
        description,
        story,
        goal,
        deadline,
        category,
        social_media_links,
        user.id,
    )
    await header_img.close()
    return campaign.id


@campaign_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Retrieve user's campaigns",
    response_model=list[schemas.CampaignResponse],
)
async def retrieve_my_campaigns(
    db: Annotated[AsyncSession, Depends(session)],
    user: Annotated[User, Depends(validate_user_access_token)],
) -> list[schemas.CampaignResponse]:
    user_campaigns = await service.retrieve_user_campaigns(db, user.id)
    campaigns_response = []
    for campaign in user_campaigns:
        amt_reached_in_percent = (
            (campaign.amt_reached / campaign.goal) * 100 if campaign.goal else 0.0
        )
        campaigns_response.append(
            schemas.CampaignResponse(
                id=campaign.id,
                title=campaign.title,
                description=campaign.description,
                image=b64encode(campaign.header_img).decode(),
                goal=campaign.goal,
                amt_reached=campaign.amt_reached,
                percent_reached=amt_reached_in_percent,
                category=campaign.category,
                no_of_reactions=campaign.no_of_reactions,
                no_of_donors=campaign.no_of_supporters,
                deadline=campaign.deadline,
            )
        )
    return campaigns_response


@campaign_router.patch(
    "/{campaign_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=None,
    dependencies=[Depends(dependencies.validate_user_created_campaign)],
    summary="Update a campaign",
)
async def update_campaign(
    db: Annotated[AsyncSession, Depends(session)],
    campaign: Annotated[Campaign, Depends(dependencies.validate_campaign_exist)],
    title: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    story: Annotated[str | None, Form()] = None,
    goal: Annotated[int | None, Form()] = None,
    deadline: Annotated[NaiveDatetime | None, Form()] = None,
    category: Annotated[list[str] | None, Form()] = None,
    social_media_links: Annotated[list[str] | None, Form()] = None,
    progress: Annotated[CampaignProgress | None, Form()] = None,
    header_img: Annotated[UploadFile | None, Form()] = None,
) -> None:
    await service.update_campaign(
        db,
        campaign,
        title,
        await header_img.read() if header_img else None,
        description,
        story,
        goal,
        deadline,
        category,
        social_media_links,
        progress,
    )
    return


@campaign_router.delete(
    "/{campaign_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependencies.validate_user_created_campaign)],
    summary="Delete a campain",
)
async def delete_campaign(
    db: Annotated[AsyncSession, Depends(session)],
    campaign: Annotated[Campaign, Depends(dependencies.validate_campaign_exist)],
) -> None:
    await service.delete_campaign(db, campaign)
    return


@campaign_router.post(
    "/{campaign_id}/like",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(dependencies.validate_user_not_already_reacted_to_campaign)],
    response_model=None,
    summary="React to a campaign",
)
async def react_to_campaign(
    db: Annotated[AsyncSession, Depends(session)],
    campaign: Annotated[Campaign, Depends(dependencies.validate_campaign_exist)],
    user: Annotated[User, Depends(validate_user_access_token)],
) -> None:
    await service.user_reaction_to_campaign(db, campaign, user)
    return


@campaign_router.get(
    "/{campaign_id}/qr-code",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(dependencies.validate_user_created_campaign)],
    summary="Generate qr-code for a campaign",
    responses={status.HTTP_201_CREATED: {"content": {"image/png": {}}}},
)
async def generate_qr_code(
    data: schemas.GenerateCampaignQRCodeRequest,
):
    campaign_url = str(data.full_url_to_campaign_page)
    buffer = BytesIO()
    segno.make_qr(campaign_url).save(buffer, scale=10, kind="png")
    buffer.seek(0)

    return Response(content=buffer.getvalue(), media_type="image/png")


@campaign_router.post(
    "/{campaign_id}/beneficiary{email}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Add a beneficiary to a campaign",
    dependencies=[Depends(dependencies.validate_user_created_campaign)],
)
async def add_beneficiary(
    db: Annotated[AsyncSession, Depends(session)],
    campaign: Annotated[Campaign, Depends(dependencies.validate_campaign_exist)],
    email: str,
) -> None:
    beneficiary = await user_service.check_user_exists_by_email(db, email)
    if not beneficiary:
        raise user_exceptions.UserNotFound()
    await service.add_beneficiary_to_campaign(db, campaign, user_id=beneficiary.id)
    return None


@campaign_router.post(
    "/feed-post/{feed_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependencies.validate_user_not_already_reacted_to_feed_post)],
    response_model=None,
    summary="React to a campaign's feed post",
)
async def react_to_feed_post(
    db: Annotated[AsyncSession, Depends(session)],
    feed_post: Annotated[FeedPost, Depends(dependencies.validate_feed_post_exist)],
    user: Annotated[User, Depends(validate_user_access_token)],
) -> None:
    await service.user_reaction_to_feed_post(db, feed_post, user)
    return


@campaign_router.post(
    "/{campaign_id}/feed-post",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.FeedResponse,
    dependencies=[Depends(dependencies.validate_user_created_campaign)],
    summary="Create a campaign feed post",
)
async def create_feed_post(
    db: Annotated[AsyncSession, Depends(session)],
    campaign: Annotated[Campaign, Depends(dependencies.validate_campaign_exist)],
    user: Annotated[User, Depends(validate_user_access_token)],
    text: Annotated[str, Form()],
    media: list[UploadFile] | None = None,
) -> schemas.FeedResponse:
    # TODO: Send feed posts to donors' emails
    feed_post = await service.create_feed_post(
        db,
        text,
        [await media.read() for media in media] if media else None,
        user.id,
        campaign,
    )
    return schemas.FeedResponse(
        id=feed_post.id,
        text=feed_post.text,
        media=[
            b64encode(feed_post_medium_bytes).decode()
            for feed_post_medium_bytes in feed_post.media
        ]
        if feed_post.media
        else None,
        no_of_reactions=feed_post.no_of_reactions,
    )


@campaign_router.patch(
    "/{campaign_id}/feed-post/{feed_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.FeedResponse,
    dependencies=[
        Depends(dependencies.validate_user_created_campaign),
        Depends(dependencies.validate_user_created_feed_post),
    ],
)
async def update_feed_post(
    db: Annotated[AsyncSession, Depends(session)],
    feed_post: Annotated[FeedPost, Depends(dependencies.validate_feed_post_exist)],
    text: Annotated[str | None, Form()] = None,
    media: list[UploadFile] | None = None,
):
    await service.update_feed_post(
        db,
        feed_post,
        text,
        [await media.read() for media in media] if media else None,
    )
    return schemas.FeedResponse(
        id=feed_post.id,
        text=feed_post.text,
        media=[
            b64encode(feed_post_medium_bytes).decode()
            for feed_post_medium_bytes in feed_post.media
        ]
        if feed_post.media
        else None,
        no_of_reactions=feed_post.no_of_reactions,
    )


@campaign_router.delete(
    "/{campaign_id}/feed-post/{feed_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    dependencies=[
        Depends(dependencies.validate_user_created_campaign),
        Depends(dependencies.validate_user_created_feed_post),
    ],
    summary="Delete a campaign feed post",
)
async def delete_feed_post(
    db: Annotated[AsyncSession, Depends(session)],
    feed_post: Annotated[FeedPost, Depends(dependencies.validate_feed_post_exist)],
) -> None:
    await service.delete_feed_post(db, feed_post)
    return


@campaign_router.post(
    "/{campaign_id}/donation",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependencies.validate_campaign_exist)],
    summary="Save information on a donation",
)
async def save_donation(
    db: Annotated[AsyncSession, Depends(session)],
    campaign: Annotated[Campaign, Depends(dependencies.validate_campaign_exist)],
    data: schemas.SaveDonationRequest,
):
    await service.create_donation(
        db,
        data.payaza_reference,
        data.transaction_reference,
        data.amount_received,
        data.name,
        data.social_media_links,
        data.anonymous,
        data.recovery_acct_no,
        data.recovery_acct_bank,
        data.recovery_acct_name,
        campaign,
    )
    return


@campaign_router.get(
    "/{campaign_id}/donation",
    summary="Get all donations made to a campaign",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.DonationResponse],
)
async def get_campaign_donations(
    campaign: Annotated[Campaign, Depends(dependencies.validate_campaign_exist)],
) -> list[schemas.DonationResponse]:
    donations = await campaign.awaitable_attrs.donations
    donations_response: list[schemas.DonationResponse] = []
    for donation in donations:
        donations_response.append(
            schemas.DonationResponse(
                id=donation.id,
                anonymous=donation.anonymous,
                name=donation.name if donation.anonymous else None,
                social_media_link=donation.social_media_links
                if donation.anonymous
                else None,
                amount=donation.amount,
            )
        )
    return donations_response
