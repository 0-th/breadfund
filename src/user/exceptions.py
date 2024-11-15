from src.exceptions import NotAuthenticated, NotFound


class InvalidAccessToken(NotAuthenticated):
    DETAIL = "Invalid Token."

    def __init__(self, scopes=""):
        if scopes != "" or scopes != "Bearer":
            super().__init__(headers={"WWW-Authenticated": f'Bearer scope="{scopes}"'})
        super().__init__(headers={"WWW-Authenticated": "Bearer"})


class UserNotFound(NotFound):
    DETAIL = "User Not Found."
