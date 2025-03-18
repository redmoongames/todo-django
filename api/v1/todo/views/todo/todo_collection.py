from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from typing import Optional, Union, List, Dict, Any
import json

from api.v1.todo.utils.responses import json_success, json_error, handle_exception
from api.v1.todo.services import TodoService
from api.v1.todo.constants import TodoStatus
from api.v1.todo.serializers import TodoSerializer


@method_decorator(login_required, name='dispatch')
class TodoCollectionView(View):
    """
    Handles collection operations for todos within a dashboard.
    
    Endpoints:
    - GET /api/v1/todo/dashboards/{dashboard_id}/todos/ - List todos with optional filtering
    - POST /api/v1/todo/dashboards/{dashboard_id}/todos/ - Create a new todo
    
    Query Parameters for GET:
    - status: Filter by todo status ('pending' or 'completed')
    - tag_id: Filter by tag ID
    - sort_by: Field to sort by (created_at, due_date, priority, title)
      Prefix with '-' for descending order (e.g. '-due_date')
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = TodoService()
        self.serializer = TodoSerializer()
        self.allowed_sort_fields = ["created_at", "due_date", "priority", "title"]
    
    def get(self, request: HttpRequest, dashboard_id: int) -> HttpResponse:
        """
        List todos in a dashboard with optional filtering.
        
        Returns:
            JSON response with todos list
        """
        try:
            params = self._validate_query_params(request)
        except ValueError as e:
            return json_error(f"Invalid query parameters. {str(e)}", status=400)
        
        try:
            todos = self.service.get_dashboard_todos(
                dashboard_id=dashboard_id,
                status=params['status'],
                tag_id=params['tag_id'],
                sort_by=params['sort_by']
            )
        except Exception as e:
            return handle_exception(e)
        
        try:
            todo_list = self.serializer.serialize_many(todos)
            return json_success({'todos': todo_list})
        except Exception as e:
            return handle_exception(e)
    
    def post(self, request: HttpRequest, dashboard_id: int) -> HttpResponse:
        """
        Create a new todo in the specified dashboard.
        
        Expects a JSON payload with todo properties.
        
        Returns:
            JSON response with the created todo object
        """
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return json_error(f"Invalid JSON format: {str(e)}", status=400)
        
        try:
            todo = self.service.create_todo(dashboard_id=dashboard_id, data=data)
        except Exception as e:
            return handle_exception(e)
            
        try:
            serialized_todo = self.serializer.serialize(todo)
            return json_success(serialized_todo, status=201)
        except Exception as e:
            return handle_exception(e) 
    
    def _validate_query_params(self, request: HttpRequest) -> Dict[str, Any]:
        """Validate and process query parameters."""
        status: Optional[str] = request.GET.get('status')
        tag_id: Optional[str] = request.GET.get('tag_id')
        sort_by: Optional[str] = request.GET.get('sort_by')
        
        if status and status not in [TodoStatus.PENDING, TodoStatus.COMPLETED]:
            raise ValueError(f"Invalid status value. Must be one of: {TodoStatus.PENDING}, {TodoStatus.COMPLETED}")
        
        if sort_by and sort_by.lstrip('-') not in self.allowed_sort_fields:
            raise ValueError(f"Invalid sort_by value. Must be one of: {', '.join(self.allowed_sort_fields)}")
        
        if tag_id and not tag_id.isdigit():
            raise ValueError("Invalid tag_id. Must be a number")
        
        return {
            'status': status,
            'tag_id': int(tag_id) if tag_id else None,
            'sort_by': sort_by
        }
    