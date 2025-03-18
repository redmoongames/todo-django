import json
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from api.v1.todo.utils.responses import json_success, json_error
from api.v1.todo.services import DashboardService, PermissionService
from api.v1.todo.serializers import DashboardSerializer
from api.v1.todo.exceptions import APIError


@method_decorator(login_required, name='dispatch')
class DashboardDetailView(View):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.dashboard_service = DashboardService()
        self.serializer = DashboardSerializer()
    
    def get(self, request: HttpRequest, dashboard_id: int) -> HttpResponse:
        try:
            permission_service = PermissionService(request)
            dashboard = permission_service.validate_dashboard_access(dashboard_id)
                
            serialized_data = self.serializer.serialize(dashboard)
            return json_success({"dashboard": serialized_data})
        except APIError as e:
            return json_error(e.message, status=e.status)
        except Exception as e:
            return json_error(f"Failed to retrieve dashboard: {str(e)}", status=500)
    
    def put(self, request: HttpRequest, dashboard_id: int) -> HttpResponse:
        try:
            permission_service = PermissionService(request)
            dashboard = permission_service.validate_dashboard_edit_permission(dashboard_id)
                
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
                
            print(f"PUT received data: {data}")
            
            update_data = {}
            
            if 'title' in data:
                update_data['title'] = data['title']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'is_public' in data:
                update_data['is_public'] = data['is_public']
            
            print(f"Update data: {update_data}")
            
            dashboard = self.dashboard_service.update_dashboard(dashboard_id, update_data)
            
            serialized_data = self.serializer.serialize(dashboard)
            return json_success({"dashboard": serialized_data})
        except json.JSONDecodeError:
            return json_error("Invalid JSON format", status=400)
        except APIError as e:
            return json_error(e.message, status=e.status)
        except Exception as e:
            return json_error(f"Failed to update dashboard: {str(e)}", status=500)
    
    def delete(self, request: HttpRequest, dashboard_id: int) -> HttpResponse:
        try:
            permission_service = PermissionService(request)
            dashboard = permission_service.validate_dashboard_owner_permission(dashboard_id)
        
            self.dashboard_service.delete_dashboard(dashboard_id)
            return json_success({"message": "Dashboard deleted successfully"})
        except APIError as e:
            return json_error(e.message, status=e.status)
        except Exception as e:
            return json_error(f"Failed to delete dashboard: {str(e)}", status=500) 