from typing import Any
from django.http import HttpRequest, HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from api.v1.todo.services import DashboardService
from api.v1.todo.serializers import DashboardSerializer
from api.v1.todo.utils.responses import json_success, json_error
from api.v1.todo.exceptions import APIError


@method_decorator(login_required, name='dispatch')
class DashboardCollectionView(View):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.dashboard_service = DashboardService()
        self.dashboard_serializer = DashboardSerializer()
    
    def get(self, request: HttpRequest) -> HttpResponse:
        try:
            dashboards = self.dashboard_service.get_user_dashboards(request.user)
        except Exception as e:
            return json_error(f"Failed to retrieve dashboards: {str(e)}", status=500)
        
        try:
            serialized_data = self.dashboard_serializer.serialize_many(dashboards)
            return json_success({"dashboards": serialized_data})
        except Exception as e:
            return json_error(f"Failed to serialize dashboards: {str(e)}", status=500)
    
    def post(self, request: HttpRequest) -> HttpResponse:
        try:
            import json
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
                
            print(f"Received data: {data}")
            
            dashboard_data = {
                'title': data.get('title'),
                'description': data.get('description', ''),
                'is_public': data.get('is_public', False)
            }
            
            print(f"Dashboard data: {dashboard_data}")
            
            dashboard = self.dashboard_service.create_dashboard(
                user_id=request.user.id,
                data=dashboard_data
            )
        except json.JSONDecodeError:
            return json_error("Invalid JSON format", status=400)
        except APIError as e:
            return json_error(e.message, status=e.status)
        except Exception as e:
            return json_error(f"Failed to create dashboard: {str(e)}", status=500)
        
        try:
            serialized_data = self.dashboard_serializer.serialize(dashboard)
            return json_success({"dashboard": serialized_data})
        except Exception as e:
            return json_error(f"Failed to serialize dashboard: {str(e)}", status=500) 