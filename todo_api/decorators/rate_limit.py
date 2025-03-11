from functools import wraps
from typing import Callable, Any
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.core.cache import cache

def rate_limit(key_prefix: str, limit: int = 5, period: int = 60) -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapped_view(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
            key = f"{key_prefix}:{client_ip}"
            
            requests_made = cache.get(key, 0)
            
            if requests_made >= limit:
                return JsonResponse(
                    {'error': 'Too many requests. Please try again later.'},
                    status=429
                )
            
            cache.set(key, requests_made + 1, timeout=period)
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator
