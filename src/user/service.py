from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.campaign.models import Campaign, Donation
from src.user.models import User


async def check_user_exists_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    query_scalars = await db.scalars(select(User).where(User.id == user_id))
    return query_scalars.one_or_none()


async def check_user_exists_by_email(db: AsyncSession, email: str) -> User | None:
    query_scalars = await db.scalars(select(User).where(User.email == email))
    return query_scalars.one_or_none()


async def create_donation(
    db: AsyncSession,
    payaza_reference: str,
    transaction_reference: str,
    amount_received: float,
    name: str,
    social_media_link: list[str] | None,
    anonymous: bool,
    recovery_acct_no: int,
    recovery_acct_bank: str,
    recovery_acct_name: str,
    campaign: Campaign,
) -> None:
    donation = Donation(
        anonymous=anonymous,
        payaza_reference=payaza_reference,
        transaction_reference=transaction_reference,
        name=name,
        social_media_link=social_media_link,
        recovery_acct_no=recovery_acct_no,
        recovery_acct_bank=recovery_acct_bank,
        recovery_acct_name=recovery_acct_name,
        campaign=campaign,
        amount=amount_received,
    )

    campaign.no_of_supporters += 1
    db.add(donation)
    db.add(campaign)
    return
