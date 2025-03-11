"""Authentication views for the Todo API.

This module handles user authentication operations including
registration, login, logout, token refresh, and token verification.
"""
from __future__ import annotations

import json
from typing import Dict, Any, Tuple

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.cache import cache
import jwt

from .decorators import jwt_authentication_required, rate_limit
from .utils import jwt_service
from .utils.jwt_service import TokenType
from .utils.password_service import password_service


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def error_response(message: str, status_code: int = 400) -> JsonResponse:
    return JsonResponse(
        {
            'success': False,
            'error': message
        }, 
        status=status_code
    )


def success_response(data: Dict[str, Any], status_code: int = 200) -> JsonResponse:
    return JsonResponse(
        {
            'success': True,
            'data': data
        },
        status=status_code
    )


@csrf_exempt
@rate_limit('register', limit=5, period=60)
def register(request: HttpRequest) -> HttpResponse:
    """Register a new user on POST request. Should have a username and password."""
    if request.method != 'POST':
        return error_response('Method not allowed', status_code=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return error_response('Invalid JSON data', status_code=400)
    except Exception as e:
        return error_response(f'Failed to parse JSON data: {str(e)}', status_code=500)

    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return error_response('Username and password are required', status_code=400)

    validation_result = password_service.validate_password(password)
    if not validation_result.is_valid:
        return error_response("; ".join(validation_result.errors), status_code=400)

    if User.objects.filter(username=username).exists():
        return error_response(f'The username "{username}" is already taken.', status_code=400)

    try:
        user = User.objects.create_user(username=username, password=password)
    except Exception as e:
        return error_response(f'Failed to create user: {str(e)}', status_code=500)

    try:
        access_token, refresh_token = jwt_service.generate_token_pair(user)
    except Exception as e:
        return error_response(f'Failed to generate tokens: {str(e)}', status_code=500)

    response = success_response(
        {
            'message': 'Registration successful',
            'user': _get_user_as_dict(user),
            'tokens': {
                'access': access_token,
                'refresh': refresh_token,
                'type': 'Bearer'
            }
        },
        status_code=201
    )

    try:
        jwt_service.set_token_cookies(response, access_token, refresh_token)
    except Exception as e:
        return error_response(f'Failed to set cookies: {str(e)}', status_code=500)

    return response


@csrf_exempt
@rate_limit('login', limit=10, period=60)
def login_view(request: HttpRequest) -> HttpResponse:
    """Authenticate a user and provide access tokens by POST request."""
    if request.method != 'POST':
        return error_response('Method not allowed', status_code=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return error_response('Invalid JSON data', status_code=400)
    except Exception as e:
        return error_response(f'Failed to parse JSON data: {str(e)}', status_code=500)
    
    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return error_response('Username and password are required', status_code=400)

    user = authenticate(username=username, password=password)
    if user is None:
        return error_response('Invalid credentials provided', status_code=401)

    try:
        jwt_service.invalidate_user_tokens(user.id)
    except Exception as e:
        return error_response(f'Failed to invalidate tokens: {str(e)}', status_code=500)

    try:
        access_token, refresh_token = jwt_service.generate_token_pair(user)
    except Exception as e:
        return error_response(f'Failed to generate tokens: {str(e)}', status_code=500)

    response = success_response({
        'message': 'Authentication successful',
        'user': _get_user_as_dict(user),
        'tokens': {
            'access': access_token,
            'refresh': refresh_token,
            'type': 'Bearer'
        }
    })

    try:
        jwt_service.set_token_cookies(response, access_token, refresh_token)
    except Exception as e:
        return error_response(f'Failed to set cookies: {str(e)}', status_code=500)

    return response


@csrf_exempt
def logout_view(request: HttpRequest) -> HttpResponse:
    """Log out a user by invalidating their tokens with POST request."""
    if request.method != 'POST':
        return error_response('Method not allowed', status_code=405)

    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return error_response('Invalid authorization header format', status_code=401)

    token = auth_header.split(' ')[1]
    if not token:
        return error_response('No token provided', status_code=401)

    try:
        user_id = jwt_service.get_user_id_from_token(token)
    except jwt.InvalidTokenError:
        return error_response('Invalid token format or signature', status_code=401)
    except jwt.ExpiredSignatureError:
        return error_response('Token has expired', status_code=401)
    except Exception as e:
        return error_response(f'Failed to verify token: {str(e)}', status_code=500)

    if user_id is None:
        return error_response('Invalid token: no user ID found', status_code=401)

    try:
        jwt_service.invalidate_user_tokens(user_id)
    except Exception as e:
        return error_response(f'Failed to invalidate tokens: {str(e)}', status_code=500)

    response = success_response({
        'message': 'Successfully logged out'
    })

    try:
        jwt_service.clear_token_cookies(response)
    except Exception as e:
        return error_response(f'Failed to clear cookies: {str(e)}', status_code=500)

    return response


@csrf_exempt
def refresh_token_view(request: HttpRequest) -> HttpResponse:
    """Refresh the access token using a valid refresh token with POST request."""
    if request.method != 'POST':
        return error_response('Method not allowed', status_code=405)

    refresh_token = jwt_service.get_token_from_cookie(request, TokenType.REFRESH)
    if not refresh_token:
        return error_response('Refresh token not found', status_code=401)

    try:
        user_id = jwt_service.get_user_id_from_token(refresh_token)
    except jwt.InvalidTokenError:
        return error_response('Invalid refresh token format or signature', status_code=401)
    except jwt.ExpiredSignatureError:
        return error_response('Refresh token has expired', status_code=401)
    except Exception as e:
        return error_response(f'Failed to verify refresh token: {str(e)}', status_code=500)

    if user_id is None:
        return error_response('Invalid refresh token: no user ID found', status_code=401)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return error_response(f'User with ID {user_id} not found', status_code=401)
    except Exception as e:
        return error_response(f'Failed to get user: {str(e)}', status_code=500)

    try:
        access_token, refresh_token = jwt_service.generate_token_pair(user)
    except Exception as e:
        return error_response(f'Failed to generate new tokens: {str(e)}', status_code=500)

    response = success_response({
        'message': 'Tokens refreshed successfully',
        'tokens': {
            'access': access_token,
            'refresh': refresh_token,
            'type': 'Bearer'
        }
    })

    try:
        jwt_service.set_token_cookies(response, access_token, refresh_token)
    except Exception as e:
        return error_response(f'Failed to set cookies: {str(e)}', status_code=500)

    return response


@csrf_exempt
@rate_limit('verify', limit=30, period=60)
def verify_token_view(request: HttpRequest) -> HttpResponse:
    """Verify the validity of the access token with GET request."""
    if request.method != 'GET':
        return error_response('Method not allowed', status_code=405)

    print(f"[DEBUG] Verify token request headers: {dict(request.headers)}")
    print(f"[DEBUG] Verify token request cookies: {request.COOKIES}")
    
    # Try to get token from Authorization header
    auth_header = request.headers.get('Authorization', '')
    print(f"[DEBUG] Authorization header: {auth_header[:30] if auth_header else 'None'}...")
    
    token = None
    
    # Extract from Authorization header
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        print(f"[DEBUG] Extracted token from Authorization header: {token[:15] if token else 'None'}...")
    
    # If no token in Authorization header, try to get from cookies
    if not token and 'auth_tokens' in request.COOKIES:
        try:
            import json
            auth_tokens = json.loads(request.COOKIES['auth_tokens'])
            if isinstance(auth_tokens, dict) and 'access_token' in auth_tokens:
                token = auth_tokens['access_token']
                print(f"[DEBUG] Extracted token from cookies: {token[:15] if token else 'None'}...")
        except Exception as e:
            print(f"[DEBUG] Error extracting token from cookies: {str(e)}")
    
    if not token:
        print("[DEBUG] No token found in request")
        return error_response('No token provided in request', status_code=401)

    try:
        print("[DEBUG] Attempting to get user_id from token")
        user_id = jwt_service.get_user_id_from_token(token)
        print(f"[DEBUG] User ID from token: {user_id}")
    except jwt.InvalidTokenError as e:
        print(f"[DEBUG] Invalid token error: {str(e)}")
        return error_response('Invalid token format or signature', status_code=401)
    except jwt.ExpiredSignatureError as e:
        print(f"[DEBUG] Token expired: {str(e)}")
        return error_response('Token has expired', status_code=401)
    except Exception as e:
        print(f"[DEBUG] Unexpected error: {str(e)}")
        return error_response(f'An error occurred while verifying the token: {str(e)}', status_code=500)

    if user_id is None:
        print("[DEBUG] No user_id found in token")
        return error_response('Invalid token: no user ID found', status_code=401)

    try:
        print(f"[DEBUG] Looking up user with ID: {user_id}")
        user = User.objects.get(id=user_id)
        print(f"[DEBUG] Found user: {user.username}")
    except User.DoesNotExist:
        print(f"[DEBUG] User with ID {user_id} not found")
        return error_response(f'User with ID {user_id} not found', status_code=401)
    except Exception as e:
        print(f"[DEBUG] Error looking up user: {str(e)}")
        return error_response(f'An error occurred while verifying the token: {str(e)}', status_code=500)

    print("[DEBUG] Token verification successful")
    return success_response({
        'message': 'Token is valid',
        'user': _get_user_as_dict(user)
    })


def _get_user_as_dict(user: User) -> Dict[str, Any]:
    return {
        'id': user.id,
        'username': user.username,
        'date_joined': user.date_joined.isoformat()
    }