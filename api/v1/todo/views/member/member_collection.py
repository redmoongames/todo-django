
import json

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from api.v1.todo.utils.responses import json_success, json_error, handle_exception
from api.v1.todo.services import MemberService, PermissionService
from api.v1.todo.constants import DashboardMemberRole


@method_decorator(login_required, name='dispatch')
class MemberCollectionView(View):
    """
    Handles collection operations for dashboard members.
    
    Endpoints:
    - GET /api/v1/todo/dashboards/{dashboard_id}/members/ - List all members of a dashboard
    - POST /api/v1/todo/dashboards/{dashboard_id}/members/ - Add a new member to a dashboard
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_service = MemberService()
    
    def get(self, request: HttpRequest, dashboard_id: int) -> HttpResponse:
        """
        List all members of a dashboard.
        
        Returns:
            JSON response with members list
        """
        try:
            permission_service = PermissionService(request)
            
            permission_result = permission_service.check_dashboard_access(dashboard_id)
            if not permission_result.granted:
                return json_error(permission_result.message, status=403)
            
            members = self.member_service.get_dashboard_members(dashboard_id=dashboard_id)
            
            member_list = []
            for member in members:
                member_data = {
                    'id': member.id,
                    'user': {
                        'id': member.user.id,
                        'username': member.user.username,
                        'email': member.user.email
                    },
                    'role': member.role,
                    'joined_at': member.joined_at.isoformat()
                }
                member_list.append(member_data)
                
            return json_success({'members': member_list})
            
        except Exception as e:
            return handle_exception(e)
    
    def post(self, request: HttpRequest, dashboard_id: int) -> HttpResponse:
        """
        Add a new member to a dashboard.
        
        Expects a JSON payload with:
        - email: Email of the user to add
        - role: Member role (optional, default: 'viewer')
        
        Returns:
            JSON response with the created member object
        """
        try:
            permission_service = PermissionService(request)
            
            permission_result = permission_service.check_dashboard_owner_permission(dashboard_id)
            if not permission_result.granted:
                return json_error("Only dashboard owners can add members", status=403)
            
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                return json_error(f"Invalid JSON format: {str(e)}", status=400)
            
            if 'email' not in data:
                return json_error("Email is required", status=400)
                
            role = data.get('role', DashboardMemberRole.VIEWER)
            
            # Validate role
            if role not in [DashboardMemberRole.EDITOR, DashboardMemberRole.VIEWER]:
                return json_error(f"Invalid role. Must be one of: {DashboardMemberRole.EDITOR}, {DashboardMemberRole.VIEWER}", status=400)
            
            member = self.member_service.add_member(
                dashboard_id=dashboard_id,
                email=data['email'],
                role=role
            )
            
            member_data = {
                'id': member.id,
                'user': {
                    'id': member.user.id,
                    'username': member.user.username,
                    'email': member.user.email
                },
                'role': member.role,
                'joined_at': member.joined_at.isoformat()
            }
            
            return json_success(member_data, status=201)
            
        except Exception as e:
            return handle_exception(e) 