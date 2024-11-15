from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import LargeBinary, String

from src.constants import SA_RELATIONS_CASCADE_OPTIONS
from src.database import Base, CommonFieldsMixin, TimestampMixin


class Campaign(CommonFieldsMixin, TimestampMixin, Base):
    __tablename__ = "campaign"
    creator_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    title: Mapped[str]
    header_img: Mapped[bytes]
    description: Mapped[str]
    story: Mapped[str]
    goal: Mapped[int] = mapped_column(BigInteger)
    amt_reached: Mapped[int] = mapped_column(BigInteger, init=False)
    deadline: Mapped[datetime | None]
    category: Mapped[list[str]] = mapped_column(ARRAY(String, zero_indexes=True))
    social_media_links: Mapped[list[str]] = mapped_column(
        ARRAY(String, zero_indexes=True)
    )
    donations: Mapped[list["Donation"]] = relationship(
        back_populates="campaign",
        passive_deletes=True,
        init=False,
        cascade="save-update, merge, expunge, delete",
    )
    feed_posts: Mapped[list["FeedPost"]] = relationship(
        back_populates="campaign",
        passive_deletes=True,
        init=False,
        cascade=SA_RELATIONS_CASCADE_OPTIONS,
    )
    user_reactions: Mapped[list["UserCampaignReaction"]] = relationship(
        back_populates="campaign",
        passive_deletes=True,
        init=False,
        cascade=SA_RELATIONS_CASCADE_OPTIONS,
    )
    no_of_supporters: Mapped[int] = mapped_column(default=0)
    no_of_reactions: Mapped[int] = mapped_column(default=0)
    beneficiary_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), init=False
    )


class Donation(CommonFieldsMixin, TimestampMixin, Base):
    __tablename__ = "donation"
    anonymous: Mapped[bool] = mapped_column()
    name: Mapped[str | None]
    social_media_link: Mapped[list[str]] = mapped_column(
        ARRAY(String, zero_indexes=True)
    )
    donor_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    recovery_acct_no: Mapped[int]
    recovery_acct_bank: Mapped[str]
    recovery_acct_name: Mapped[str]
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaign.id", ondelete="SET NULL"), init=False
    )
    campaign: Mapped[Campaign] = relationship(
        back_populates="donations", foreign_keys=campaign_id
    )
    amount: Mapped[int] = mapped_column(BigInteger, default=0, init=False)


class FeedPost(CommonFieldsMixin, TimestampMixin, Base):
    __tablename__ = "feedpost"
    text: Mapped[str]
    media: Mapped[list[bytes] | None] = mapped_column(
        ARRAY(LargeBinary, zero_indexes=True)
    )
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaign.id", ondelete="CASCADE"), init=False
    )
    campaign: Mapped[Campaign] = relationship(
        back_populates="feed_posts", foreign_keys=campaign_id
    )
    user_reactions: Mapped[list["UserFeedPostReaction"]] = relationship(
        back_populates="feed_post",
        init=False,
        passive_deletes=True,
        cascade=SA_RELATIONS_CASCADE_OPTIONS,
    )
    no_of_reactions: Mapped[int] = mapped_column(default=0)


class UserCampaignReaction(CommonFieldsMixin, TimestampMixin, Base):
    __tablename__ = "user_campaign_reaction"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaign.id", ondelete="CASCADE")
    )
    campaign: Mapped[Campaign] = relationship(
        back_populates="user_reactions", foreign_keys=campaign_id, init=False
    )


class UserFeedPostReaction(CommonFieldsMixin, TimestampMixin, Base):
    __tablename__ = "user_feed_post_reaction"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    feed_post_id: Mapped[UUID] = mapped_column(
        ForeignKey("feedpost.id", ondelete="CASCADE")
    )
    feed_post: Mapped[FeedPost] = relationship(
        back_populates="user_reactions", foreign_keys=feed_post_id, init=False
    )
