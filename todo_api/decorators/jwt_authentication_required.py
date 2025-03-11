from functools import wraps
from typing import Callable, Any
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib.auth.models import User
import jwt

from ..utils.jwt_service import jwt_service

def jwt_authentication_required(view_func: Callable) -> Callable:
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'No token provided'}, status=401)

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, jwt_service.Config.SECRET_KEY, algorithms=[jwt_service.Config.ALGORITHM])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        if payload.get('type') != 'access':
            return JsonResponse({'error': 'Invalid token type'}, status=401)

        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        request.user = user
        return view_func(request, *args, **kwargs)

    return wrapper
