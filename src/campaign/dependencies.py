from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.campaign import exceptions, service
from src.campaign.models import Campaign, FeedPost
from src.database import session
from src.user.dependencies import validate_user_access_token
from src.user.models import User


async def validate_campaign_exist(
    db: Annotated[AsyncSession, Depends(session)], campaign_id: UUID
) -> Campaign:
    campaign = await service.get_campaign(db, campaign_id)
    if campaign:
        return campaign
    raise exceptions.CampaignNotFound()


async def validate_feed_post_exist(
    db: Annotated[AsyncSession, Depends(session)], feed_post_id: UUID
):
    feed_post = await service.get_feed_post(db, feed_post_id)
    if feed_post:
        return feed_post
    raise exceptions.FeedNotFound()


async def validate_user_not_already_reacted_to_campaign(
    db: Annotated[AsyncSession, Depends(session)],
    campaign: Annotated[Campaign, Depends(validate_campaign_exist)],
    user: Annotated[User, Depends(validate_user_access_token)],
) -> None:
    if service.user_reaction_to_campaign_exists(db, campaign, user):
        raise exceptions.UserAlreadyReacted()
    return


async def validate_user_not_already_reacted_to_feed_post(
    db: Annotated[AsyncSession, Depends(session)],
    feed_post: Annotated[FeedPost, Depends(validate_feed_post_exist)],
    user: Annotated[User, Depends(validate_user_access_token)],
) -> None:
    if service.user_reaction_to_feed_post_exists(db, feed_post, user):
        raise exceptions.UserAlreadyReacted()
    return


async def validate_user_created_campaign(
    campaign: Annotated[Campaign, Depends(validate_campaign_exist)],
    user: Annotated[User, Depends(validate_user_access_token)],
):
    if user.id != campaign.creator_id:
        raise exceptions.UserNotCampaignCreator()
    return user


async def validate_user_created_feed_post(
    feed_post: Annotated[FeedPost, Depends(validate_feed_post_exist)],
    user: Annotated[User, Depends(validate_user_access_token)],
):
    if user.id != feed_post.creator_id:
        raise exceptions.UserNotFeedPostCreator()
    return user
