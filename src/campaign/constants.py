from typing import Final


class ErrorMessage:
    CAMPAIGN_NOT_FOUND: Final[str] = "Campaign Not Found."
    FEED_NOT_FOUND: Final[str] = "Feed Post Not Found."
    USER_ALREADY_REACTED: Final[str] = "User Already Reacted."
    USER_NOT_CAMPAIGN_CREATOR: Final[str] = "User Not Campaign Creator."
    USER_NOT_FEED_POST_CREATOR: Final[str] = "User Not Feed Post Creator."
