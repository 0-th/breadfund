from enum import Enum
from typing import Final, final

DB_NAMING_CONVENTION: Final[dict[str, str]] = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class Environment(str, Enum):
    LOCAL = "LOCAL"
    STAGING = "STAGING"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"

    @property
    @final
    def is_debug(self) -> bool:
        return self in (self.LOCAL, self.STAGING, self.TESTING)

    @property
    @final
    def is_testing(self) -> bool:
        return self == self.TESTING

    @property
    @final
    def is_deployed(self) -> bool:
        return self in (self.STAGING, self.PRODUCTION)


# cascade option - refresh-expire has to be excluded for async sessions.
# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#asyncio-orm-avoid-lazyloads
SA_RELATIONS_CASCADE_OPTIONS: Final[str] = (
    "save-update, merge, expunge, delete, delete-orphan"
)
