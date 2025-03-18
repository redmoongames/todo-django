from typing import Any, Dict, Optional

from django.http import JsonResponse as DjangoJsonResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from api.v1.todo.exceptions import APIError


def json_success(data: Optional[Dict[str, Any]] = None, status: int = 200) -> DjangoJsonResponse:
    """
    Create a standardized success JSON response.
    
    Args:
        data: Optional data to include in the response
        status: HTTP status code (default: 200)
        
    Returns:
        JsonResponse with standard success format
    """
    response_data: Dict[str, Any] = {
        "status": "success"
    }
    
    if data is not None:
        response_data["data"] = data
        
    return DjangoJsonResponse(response_data, status=status)


def json_error(message: str, status: int = 400) -> DjangoJsonResponse:
    """
    Create a standardized error JSON response.
    
    Args:
        message: Error message
        status: HTTP status code (default: 400)
        
    Returns:
        JsonResponse with standard error format
    """
    response_data: Dict[str, Any] = {
        "status": "error",
        "message": message
    }
        
    return DjangoJsonResponse(response_data, status=status)


def handle_exception(e: Exception) -> DjangoJsonResponse:
    """
    Convert various exception types to appropriate JSON responses.
    
    Args:
        e: The exception to handle
        
    Returns:
        JsonResponse with appropriate error data and status code
    """
    if isinstance(e, APIError):
        return json_error(e.message, status=e.status)
    if isinstance(e, ValidationError):
        return json_error(str(e), status=400)
    if isinstance(e, IntegrityError):
        return json_error("Database integrity error", status=400)
    return json_error(f"Internal server error: {str(e)}", status=500) 