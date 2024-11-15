from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.campaign.models import (
    Campaign,
    FeedPost,
    UserCampaignReaction,
    UserFeedPostReaction,
)
from src.user.models import User


async def retrieve_campaigns_with_highest_reactions_and_donors(
    db: AsyncSession, limit: int, skip: int
) -> list[Campaign]:
    query_scalars = await db.scalars(
        select(Campaign)
        .order_by(Campaign.no_of_reactions.desc(), Campaign.no_of_supporters.desc())
        .limit(limit)
        .offset(skip)
    )
    return list(query_scalars.all())


async def get_campaign(db: AsyncSession, campaign_id: UUID) -> Campaign | None:
    query_scalars = await db.scalars(select(Campaign).where(Campaign.id == campaign_id))
    return query_scalars.one_or_none()


async def get_feed_post(db: AsyncSession, feed_post_id: UUID) -> FeedPost | None:
    query_scalars = await db.scalars(
        select(FeedPost).where(FeedPost.id == feed_post_id)
    )
    return query_scalars.one_or_none()


async def create_campaign(
    db: AsyncSession,
    title: str,
    header_img: bytes,
    description: str,
    story: str,
    goal: int,
    deadline: datetime,
    category: list[str],
    social_media_links: list[str],
    creator_id: UUID,
):
    campaign = Campaign(
        title=title,
        header_img=header_img,
        description=description,
        story=story,
        goal=goal,
        deadline=deadline,
        category=category,
        social_media_links=social_media_links,
        creator_id=creator_id,
    )
    db.add(campaign)
    await db.flush()
    return campaign


async def update_campaign(
    db: AsyncSession,
    campaign: Campaign,
    title: str | None,
    header_img: bytes | None,
    description: str | None,
    story: str | None,
    goal: int | None,
    deadline: datetime | None,
    category: list[str] | None,
    social_media_links: list[str] | None,
) -> None:
    if title:
        campaign.title = title
    if header_img:
        campaign.header_img = header_img
    if description:
        campaign.description = description
    if story:
        campaign.story = story
    if goal:
        campaign.goal = goal
    if deadline:
        campaign.deadline = deadline
    if category:
        campaign.category = category
    if social_media_links:
        campaign.social_media_links = social_media_links

    db.add(campaign)
    return


async def user_reaction_to_campaign_exists(
    db: AsyncSession, campaign: Campaign, user: User
) -> bool:
    query_scalars = await db.scalars(
        select(UserCampaignReaction).where(
            UserCampaignReaction.campaign_id == campaign.id,
            UserCampaignReaction.user_id == user.id,
        )
    )
    user_campaign_reaction = query_scalars.one_or_none()
    if user_campaign_reaction:
        return True
    return False


async def user_reaction_to_campaign(
    db: AsyncSession, campaign: Campaign, user: User
) -> None:
    user_campaign_reaction = UserCampaignReaction(
        user_id=user.id, campaign_id=campaign.id
    )
    campaign.no_of_reactions += 1

    db.add(user_campaign_reaction)
    db.add(campaign)
    return


async def delete_campaign(db: AsyncSession, campaign: Campaign) -> None:
    await db.delete(campaign)
    return


async def add_beneficiary_to_campaign(
    db: AsyncSession, campaign: Campaign, user_id: UUID
) -> None:
    campaign.beneficiary_user_id = user_id
    db.add(campaign)
    return


async def create_feed_post(
    db: AsyncSession,
    text: str,
    media: list[bytes] | None,
    creator_id: UUID,
    campaign: Campaign,
) -> FeedPost:
    feed_post = FeedPost(
        text=text, media=media, creator_id=creator_id, campaign=campaign
    )
    db.add(feed_post)
    await db.flush()
    return feed_post


async def update_feed_post(
    db: AsyncSession, feed_post: FeedPost, text: str | None, media: list[bytes] | None
) -> None:
    if text:
        feed_post.text = text
    if media:
        feed_post.media = media

    db.add(feed_post)
    return


async def user_reaction_to_feed_post_exists(
    db: AsyncSession, feed_post: FeedPost, user: User
) -> bool:
    query_scalars = await db.scalars(
        select(UserFeedPostReaction).where(
            UserFeedPostReaction.feed_post_id == feed_post.id,
            UserFeedPostReaction.user_id == user.id,
        )
    )
    user_feed_post_reation = query_scalars.one_or_none()
    if user_feed_post_reation:
        return True
    return False


async def user_reaction_to_feed_post(
    db: AsyncSession, feed_post: FeedPost, user: User
) -> None:
    user_feed_post_reaction = UserFeedPostReaction(
        user_id=user.id, feed_post_id=feed_post.id
    )
    feed_post.no_of_reactions += 1

    db.add(user_feed_post_reaction)
    db.add(feed_post)
    return


async def delete_feed_post(db: AsyncSession, feed_post: FeedPost) -> None:
    await db.delete(feed_post)
