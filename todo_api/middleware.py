from django.http import HttpRequest
from django.urls import resolve, Resolver404

class TrailingSlashMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # Try to resolve the URL with and without trailing slash
        path = request.path
        try:
            resolve(path)
        except Resolver404:
            # If URL doesn't resolve, try the opposite (with/without slash)
            if path.endswith('/'):
                path = path[:-1]
            else:
                path = path + '/'
            
            try:
                resolve(path)
                # If the other version exists, use that path but keep the original request
                request.path = path
                request.path_info = path
            except Resolver404:
                pass

        return self.get_response(request) 