"""Todo items views for the Todo API.

This module handles CRUD operations for todo items.
"""

import json
from typing import Dict, Any, Union
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone

from .models import Task, Label
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
def task_items(request: HttpRequest) -> JsonResponse:
    """
    Handle CRUD operations for task items
    GET: List all tasks for the user with optional filtering
    POST: Create a new task
    """
    user = request.user
    
    # GET request - list tasks with optional filtering
    if request.method == 'GET':
        # Start with all tasks for this user
        tasks_query = Task.objects.filter(user=user)
        
        # Apply filters if provided
        priority = request.GET.get('priority')
        if priority:
            tasks_query = tasks_query.filter(priority=priority)
        
        completed = request.GET.get('completed')
        if completed is not None:
            completed_bool = completed.lower() == 'true'
            tasks_query = tasks_query.filter(completed=completed_bool)
        
        label_id = request.GET.get('label')
        if label_id:
            tasks_query = tasks_query.filter(labels__id=label_id)
        
        # Get the filtered tasks
        tasks = tasks_query.distinct()
        
        # Return the tasks
        return success_response({
            'items': [task.to_dict() for task in tasks]
        })
    
    # POST request - create a new task
    elif request.method == 'POST':
        try:
            data = _parse_json_request(request)
            if data is None:
                return error_response("Invalid JSON in request body")
            
            # Required fields
            title = data.get('title')
            if not title:
                return error_response("Title is required")
            
            # Optional fields with defaults
            description = data.get('description', '')
            priority = data.get('priority', 'medium')
            
            # Validate priority
            valid_priorities = [choice[0] for choice in Task.PRIORITY_CHOICES]
            if priority not in valid_priorities:
                return error_response(f"Invalid priority. Choose from: {', '.join(valid_priorities)}")
            
            # Create the task
            task = Task.objects.create(
                user=user,
                title=title,
                description=description,
                priority=priority,
                completed=data.get('completed', False)
            )
            
            # Add labels if provided
            label_ids = data.get('labels', [])
            if label_ids:
                # Get labels that belong to this user
                labels = Label.objects.filter(id__in=label_ids, user=user)
                task.labels.set(labels)
            
            return success_response(task.to_dict(), 201)
                
        except Exception as e:
            return error_response(f"Error creating task: {str(e)}")
    
    # Method not allowed
    return error_response("Method not allowed", 405)


@csrf_exempt
@jwt_authentication_required
def task_item_by_id(request: HttpRequest, id: int) -> JsonResponse:
    """
    Handle operations on a specific task item
    GET: Get task details
    PUT: Update task
    DELETE: Delete task
    """
    user = request.user
    
    # Try to get the task
    try:
        task = Task.objects.get(id=id, user=user)
    except Task.DoesNotExist:
        return error_response("Task not found", 404)
    
    # GET request - get task details
    if request.method == 'GET':
        return success_response(task.to_dict())
    
    # PUT request - update task
    elif request.method == 'PUT':
        try:
            data = _parse_json_request(request)
            if data is None:
                return error_response("Invalid JSON in request body")
            
            # Update fields if provided
            if 'title' in data:
                task.title = data['title']
            
            if 'description' in data:
                task.description = data['description']
            
            if 'priority' in data:
                # Validate priority
                valid_priorities = [choice[0] for choice in Task.PRIORITY_CHOICES]
                if data['priority'] not in valid_priorities:
                    return error_response(f"Invalid priority. Choose from: {', '.join(valid_priorities)}")
                task.priority = data['priority']
            
            if 'completed' in data:
                # If completing the task, set completed_at timestamp
                if data['completed'] and not task.completed:
                    task.completed_at = timezone.now()
                # If un-completing the task, clear completed_at
                elif not data['completed'] and task.completed:
                    task.completed_at = None
                task.completed = data['completed']
            
            # Update labels if provided
            if 'labels' in data:
                # Get labels that belong to this user
                labels = Label.objects.filter(id__in=data['labels'], user=user)
                task.labels.set(labels)
            
            task.save()
            return success_response(task.to_dict())
                
        except Exception as e:
            return error_response(f"Error updating task: {str(e)}")
    
    # DELETE request - delete task
    elif request.method == 'DELETE':
        task.delete()
        return success_response({"message": "Task deleted successfully"})
    
    # Method not allowed
    return error_response("Method not allowed", 405)


def _parse_json_request(request: HttpRequest) -> Union[Dict[str, Any], None]:
    """
    Parse JSON from request body
    Returns None if parsing fails
    """
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None
