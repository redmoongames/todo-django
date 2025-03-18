from typing import Any, Dict, Optional
from django.http import JsonResponse as DjangoJsonResponse
from django.contrib.auth.models import User


class JsonResponse:
    @staticmethod
    def success(data: Optional[Dict[str, Any]] = None, status: int = 200) -> DjangoJsonResponse:
        response_data: Dict[str, Any] = {
            "status": "success"
        }
        
        if data is not None:
            response_data["data"] = data
            
        return DjangoJsonResponse(response_data, status=status)
    
    @staticmethod
    def error(message: str, status: int = 400) -> DjangoJsonResponse:
        response_data: Dict[str, Any] = {
            "status": "error",
            "message": message
        }
            
        return DjangoJsonResponse(response_data, status=status)


def get_user_data(user: User) -> Dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    } 