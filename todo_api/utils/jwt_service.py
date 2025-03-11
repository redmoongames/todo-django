"""JWT utilities for token generation and management.

This module provides utilities for JWT token generation, validation,
and cookie management in the authentication system.
"""

import json
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, Any, Tuple, Optional

import jwt
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.contrib.auth.models import User


class TokenType(Enum):
    """Enum for JWT token types."""
    ACCESS = 'access'
    REFRESH = 'refresh'


class JWTService:
    """Handles JWT token operations and management."""

    class Config:
        """JWT configuration settings."""
        SECRET_KEY: str = settings.SECRET_KEY
        ACCESS_TOKEN_EXPIRATION: timedelta = timedelta(minutes=15)
        REFRESH_TOKEN_EXPIRATION: timedelta = timedelta(days=7)
        ALGORITHM: str = 'HS256'
        COOKIE_NAME: str = 'auth_tokens'

    def __init__(self) -> None:
        self._current_time = datetime.now(timezone.utc)

    def invalidate_user_tokens(self, user_id: int) -> None:
        """Invalidate all tokens for a specific user.

        Args:
            user_id: The ID of the user whose tokens should be invalidated.
        """
        cache.delete(f"refresh_token:{user_id}")

    def invalidate_token(self, token: str) -> None:
        """Invalidate a specific token.

        Args:
            token: The token to invalidate.
        """
        try:
            payload = self.decode_token(token)
            if user_id := payload.get('user_id'):
                self.invalidate_user_tokens(user_id)
        except jwt.InvalidTokenError:
            pass  # Ignore invalid tokens

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """Extract user ID from a token if valid.

        Args:
            token: The JWT token to decode.

        Returns:
            The user ID if token is valid, None otherwise.
        """
        try:
            payload = self.decode_token(token)
            print(f"[DEBUG] Token payload: {payload}")
            
            # Try different possible field names for user_id
            user_id = None
            for field in ['user_id', 'userId', 'sub', 'id']:
                if field in payload:
                    user_id = payload[field]
                    print(f"[DEBUG] Found user_id in field '{field}': {user_id}")
                    break
            
            if user_id is None:
                print(f"[DEBUG] No user_id found in payload. Available fields: {list(payload.keys())}")
            
            return user_id
        except jwt.InvalidTokenError as e:
            print(f"[DEBUG] Invalid token error: {str(e)}")
            return None
        except Exception as e:
            print(f"[DEBUG] Unexpected error decoding token: {str(e)}")
            return None

    def extract_token_from_auth_header(self, auth_header: str) -> Optional[str]:
        """Extract token from Authorization header.

        Args:
            auth_header: The Authorization header value.

        Returns:
            The token if present and valid format, None otherwise.
        """
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

    def generate_token_pair(self, user: User) -> Tuple[str, str]:
        """Generate a pair of access and refresh tokens for a user.

        Args:
            user: The user for whom to generate tokens.

        Returns:
            A tuple containing (access_token, refresh_token).
        """
        access_token = self._create_token(
            user=user,
            token_type=TokenType.ACCESS,
            expiration_delta=self.Config.ACCESS_TOKEN_EXPIRATION
        )

        refresh_token = self._create_token(
            user=user,
            token_type=TokenType.REFRESH,
            expiration_delta=self.Config.REFRESH_TOKEN_EXPIRATION
        )

        self._store_refresh_token(user.id, refresh_token)
        return access_token, refresh_token

    def set_token_cookies(
        self,
        response: HttpResponse,
        access_token: str,
        refresh_token: str
    ) -> None:
        """Set JWT tokens as HttpOnly cookies in the response.

        Args:
            response: The HTTP response object.
            access_token: The JWT access token.
            refresh_token: The JWT refresh token.
        """
        auth_tokens = json.dumps({
            'access_token': access_token,
            'refresh_token': refresh_token
        })
        
        response.set_cookie(
            self.Config.COOKIE_NAME,
            auth_tokens,
            **self._get_cookie_options()
        )

    def clear_token_cookies(self, response: HttpResponse) -> None:
        """Clear JWT tokens from cookies.

        Args:
            response: The HTTP response object.
        """
        response.delete_cookie(self.Config.COOKIE_NAME)

    def verify_token(self, token: str, expected_type: TokenType) -> bool:
        """Verify if a token is valid and of the expected type.

        Args:
            token: The JWT token to validate.
            expected_type: The expected token type (TokenType.ACCESS or TokenType.REFRESH).

        Returns:
            True if the token is valid and of the expected type.
        """
        try:
            payload = self.decode_token(token)
            return payload.get('type') == expected_type.value
        except jwt.InvalidTokenError:
            return False

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token.

        Args:
            token: The JWT token to decode.

        Returns:
            The decoded token payload.

        Raises:
            jwt.InvalidTokenError: If the token is invalid or expired.
        """
        try:
            print(f"[DEBUG] Decoding token: {token[:15]}...")
            
            # Try to decode with verification first
            try:
                decoded = jwt.decode(
                    token,
                    self.Config.SECRET_KEY,
                    algorithms=[self.Config.ALGORITHM]
                )
                print(f"[DEBUG] Successfully decoded token with verification: {decoded}")
                return decoded
            except Exception as e:
                print(f"[DEBUG] Error decoding token with verification: {str(e)}")
                
                # If verification fails, try decoding without verification to see the payload
                try:
                    decoded_unverified = jwt.decode(
                        token,
                        options={"verify_signature": False}
                    )
                    print(f"[DEBUG] Unverified token payload: {decoded_unverified}")
                except Exception as unverified_error:
                    print(f"[DEBUG] Error decoding unverified token: {str(unverified_error)}")
                
                # Re-raise the original error
                raise e
        except Exception as e:
            print(f"[DEBUG] Error decoding token: {str(e)}")
            raise

    def _create_token(
        self,
        user: User,
        token_type: TokenType,
        expiration_delta: timedelta
    ) -> str:
        """Create a JWT token with the specified type and expiration.

        Args:
            user: The user for whom to create the token.
            token_type: The type of token (TokenType.ACCESS or TokenType.REFRESH).
            expiration_delta: The time until the token expires.

        Returns:
            The encoded JWT token string.
        """
        expiration = self._current_time + expiration_delta
        payload = self._create_token_payload(user, expiration, token_type)
        
        return jwt.encode(
            payload,
            self.Config.SECRET_KEY,
            algorithm=self.Config.ALGORITHM
        )

    def _create_token_payload(
        self,
        user: User,
        expiration: datetime,
        token_type: TokenType
    ) -> Dict[str, Any]:
        """Create a JWT token payload for a user.

        Args:
            user: The user from django.contrib.auth.models.
            expiration: The token expiration datetime.
            token_type: The type of token (TokenType.ACCESS or TokenType.REFRESH).

        Returns:
            A dictionary containing the token payload.
        """
        payload = {
            'user_id': user.id,
            'exp': expiration,
            'type': token_type.value
        }
        
        if token_type == TokenType.ACCESS:
            payload['username'] = user.username
            
        return payload

    def _store_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """Store a refresh token in the cache for blacklisting.

        Args:
            user_id: The ID of the user.
            refresh_token: The refresh token to store.
        """
        cache.set(
            f"refresh_token:{user_id}",
            refresh_token,
            timeout=int(self.Config.REFRESH_TOKEN_EXPIRATION.total_seconds())
        )

    def _get_cookie_options(self) -> Dict[str, Any]:
        """Get the options for setting secure cookies.

        Returns:
            A dictionary of cookie options.
        """
        is_development = settings.DEBUG
        same_site = 'None' if is_development else 'Strict'
        
        options = {
            'httponly': True,  # Prevent JavaScript access
            'secure': True,    # Required when SameSite is None, even in development
            'samesite': same_site,
            'max_age': int(self.Config.REFRESH_TOKEN_EXPIRATION.total_seconds()),
            'path': '/',  # Make cookie available for all paths
        }

        # In development, we don't set domain to allow cross-origin
        if not is_development and hasattr(settings, 'COOKIE_DOMAIN'):
            options['domain'] = settings.COOKIE_DOMAIN

        return options


############################
# in real project, this should service from DI container
jwt_service = JWTService()
############################
