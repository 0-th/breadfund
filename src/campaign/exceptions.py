from src.campaign.constants import ErrorMessage
from src.exceptions import BadRequest, NotFound, PermissionDenied


class CampaignNotFound(NotFound):
    DETAIL = ErrorMessage.CAMPAIGN_NOT_FOUND


class FeedNotFound(NotFound):
    DETAIL = ErrorMessage.FEED_NOT_FOUND


class UserAlreadyReacted(BadRequest):
    DETAIL = ErrorMessage.USER_ALREADY_REACTED


class UserNotCampaignCreator(PermissionDenied):
    DETAIL = ErrorMessage.USER_NOT_CAMPAIGN_CREATOR


class UserNotFeedPostCreator(PermissionDenied):
    DETAIL = ErrorMessage.USER_NOT_FEED_POST_CREATOR
