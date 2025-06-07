from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from urllib.parse import parse_qs


class JWTAuthMiddleware(BaseMiddleware):
    """
    JWT authentication middleware for WebSocket connections.
    Expects JWT token to be passed as 'token' query parameter.
    """

    def __init__(self, inner):
        super().__init__(inner)
        self.User = get_user_model()

    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token:
            try:
                # Validate the token using rest_framework_simplejwt
                access_token = AccessToken(token)
                user_id = access_token["user_id"]

                # Get the user from database
                user = await self.get_user(user_id)
                scope["user"] = user

            except (InvalidToken, TokenError, KeyError):
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    async def get_user(self, user_id):
        """
        Get user from database asynchronously.
        """
        try:
            from django.contrib.auth.models import User
            from channels.db import database_sync_to_async

            @database_sync_to_async
            def get_user_sync(user_id):
                try:
                    return User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return AnonymousUser()

            return await get_user_sync(user_id)
        except Exception:
            return AnonymousUser()


def JWTAuthMiddlewareStack(inner):
    """
    Convenience function to create JWT auth middleware stack.
    """
    return JWTAuthMiddleware(inner)
