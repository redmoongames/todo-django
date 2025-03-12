from __future__ import annotations

from typing import Dict, Any

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt


def success_response(data: Dict[str, Any], status_code: int = 200) -> JsonResponse:
    return JsonResponse(
        {
            'success': True,
            'data': data
        },
        status=status_code
    )

@csrf_exempt
def health_check(request: HttpRequest) -> HttpResponse:
    """Simple health check endpoint to verify the API is running.
    
    Returns a 200 OK response with basic server information.
    """
    import socket
    import os
    from django.conf import settings
    
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "Unable to determine"
    
    # Print debug information to server logs
    print(f"DEBUG: Health check request received")
    print(f"DEBUG: Request host: {request.get_host()}")
    print(f"DEBUG: Request META['HTTP_HOST']: {request.META.get('HTTP_HOST', 'Not provided')}")
    print(f"DEBUG: ALLOWED_HOSTS setting: {settings.ALLOWED_HOSTS}")
    
    # Get all request headers for debugging
    headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
    
    data = {
        'status': 'ok',
        'message': 'API server is running',
        'server': {
            'hostname': hostname,
            'ip_address': ip_address,
            'debug_mode': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'env_allowed_hosts': os.environ.get('ALLOWED_HOSTS', 'Not set'),
        },
        'request': {
            'method': request.method,
            'path': request.path,
            'host': request.get_host(),
            'is_secure': request.is_secure(),
            'headers': headers,
            'remote_addr': request.META.get('REMOTE_ADDR', 'Not available'),
            'http_host': request.META.get('HTTP_HOST', 'Not available'),
        }
    }
    
    return success_response(data)