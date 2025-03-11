import json
from typing import Dict, Any, Union
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import Label
from .decorators import jwt_authentication_required

def error_response(message: str, status_code: int = 400) -> JsonResponse:
    """
    Create a standardized error response
    """
    return JsonResponse(
        {"success": False, "error": message},
        status=status_code
    )

def success_response(data: Dict[str, Any], status_code: int = 200) -> JsonResponse:
    """
    Create a standardized success response
    """
    return JsonResponse(
        {"success": True, "data": data},
        status=status_code
    )

@csrf_exempt
@jwt_authentication_required
def labels(request: HttpRequest) -> JsonResponse:
    """
    Handle CRUD operations for labels
    GET: List all labels for the user
    POST: Create a new label
    """
    user = request.user
    
    # GET request - list all labels
    if request.method == 'GET':
        user_labels = Label.objects.filter(user=user)
        return success_response({
            'items': [label.to_dict() for label in user_labels]
        })
    
    # POST request - create a new label
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            color = data.get('color', 'blue')
            
            if not name:
                return error_response("Label name is required")
            
            # Check if the color is valid
            valid_colors = [choice[0] for choice in Label.LABEL_COLORS]
            if color not in valid_colors:
                return error_response(f"Invalid color. Choose from: {', '.join(valid_colors)}")
            
            # Create the label
            try:
                label = Label.objects.create(
                    user=user,
                    name=name,
                    color=color
                )
                return success_response(label.to_dict(), 201)
            except IntegrityError:
                return error_response("A label with this name already exists", 409)
                
        except json.JSONDecodeError:
            return error_response("Invalid JSON in request body")
    
    # Method not allowed
    return error_response("Method not allowed", 405)

@csrf_exempt
@jwt_authentication_required
def label_detail(request: HttpRequest, id: int) -> JsonResponse:
    """
    Handle operations on a specific label
    GET: Get label details
    PUT: Update label
    DELETE: Delete label
    """
    user = request.user
    
    # Try to get the label
    try:
        label = Label.objects.get(id=id, user=user)
    except Label.DoesNotExist:
        return error_response("Label not found", 404)
    
    # GET request - get label details
    if request.method == 'GET':
        return success_response(label.to_dict())
    
    # PUT request - update label
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            # Update fields if provided
            if 'name' in data:
                label.name = data['name']
            
            if 'color' in data:
                # Check if the color is valid
                valid_colors = [choice[0] for choice in Label.LABEL_COLORS]
                if data['color'] not in valid_colors:
                    return error_response(f"Invalid color. Choose from: {', '.join(valid_colors)}")
                label.color = data['color']
            
            try:
                label.save()
                return success_response(label.to_dict())
            except IntegrityError:
                return error_response("A label with this name already exists", 409)
                
        except json.JSONDecodeError:
            return error_response("Invalid JSON in request body")
    
    # DELETE request - delete label
    elif request.method == 'DELETE':
        label.delete()
        return success_response({"message": "Label deleted successfully"})
    
    # Method not allowed
    return error_response("Method not allowed", 405) 