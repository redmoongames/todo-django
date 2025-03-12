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
    from django.conf import settings
    
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    data = {
        'status': 'ok',
        'message': 'API server is running',
        'server': {
            'hostname': hostname,
            'ip_address': ip_address,
            'debug_mode': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
        },
        'request': {
            'method': request.method,
            'path': request.path,
            'host': request.get_host(),
            'is_secure': request.is_secure(),
        }
    }
    
    return success_response(data)