import json
from typing import Dict, Any
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .utils import JsonResponse, get_user_data


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    try:
        data = json.loads(request.body)
        username = data.get("username")  
        password = data.get("password")
        
        if not username or not password:
            return JsonResponse.error("Username and password are required")
        
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
                user = authenticate(request, username=username, password=password)
            except User.DoesNotExist:
                return JsonResponse.error("User with this email does not exist")
        else:
            user = authenticate(request, username=username, password=password)
        
        if user is None:
            return JsonResponse.error("Invalid credentials")
            
        if not user.is_active:
            return JsonResponse.error("User account is disabled")
        
        login(request, user)
        
        return JsonResponse.success({
            "user": get_user_data(user),
            "session_id": request.session.session_key
        })
    except json.JSONDecodeError:
        return JsonResponse.error("Invalid JSON format")


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return JsonResponse.success({"message": "Successfully logged out"})


@csrf_exempt
@require_http_methods(["POST"])
def register_view(request: HttpRequest) -> HttpResponse:
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        
        if not username or not password:
            return JsonResponse.error("Username and password are required")
        
        if User.objects.filter(username=username).exists():
            return JsonResponse.error("Username already exists")
        
        if not email:
            return JsonResponse.error("Email address is required")
            
        if User.objects.filter(email=email).exists():
            return JsonResponse.error("Email already exists")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        login(request, user)
        
        return JsonResponse.success({
            "user": get_user_data(user),
            "session_id": request.session.session_key
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse.error("Invalid JSON format")


@require_http_methods(["GET"])
@login_required
def user_info_view(request: HttpRequest) -> HttpResponse:
    return JsonResponse.success({
        "user": get_user_data(request.user)
    })


@require_http_methods(["GET"])
def session_check_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return JsonResponse.success({
            "authenticated": True,
            "user": get_user_data(request.user)
        })
    return JsonResponse.success({"authenticated": False})
