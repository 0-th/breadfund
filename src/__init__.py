# This initialization script ensures that the `Base` class object
# that has each db class model registered in it gets imported and
# re-evaluated here. This enables it to be evaluated after the models
# definitions in the models.py file.
# This enables alembic to generate appropriate migration scripts.

from src.campaign.models import Base as CampaignBase
from src.user.models import Base as UserBase

__all__ = ["UserBase", "CampaignBase"]
