from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from typing import Dict, Any
import json

from api.v1.todo.utils.responses import json_success, json_error, handle_exception
from api.v1.todo.services import MemberService, PermissionService
from api.v1.todo.constants import DashboardMemberRole


@method_decorator(login_required, name='dispatch')
class MemberDetailView(View):
    """
    Handles operations on specific dashboard members.
    
    Endpoints:
    - PUT /api/v1/todo/dashboards/{dashboard_id}/members/{member_id}/ - Update member role
    - DELETE /api/v1/todo/dashboards/{dashboard_id}/members/{member_id}/ - Remove member from dashboard
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_service = MemberService()
    
    def put(self, request: HttpRequest, dashboard_id: int, member_id: int) -> HttpResponse:
        """
        Update a dashboard member's role.
        
        Expects a JSON payload with:
        - role: New role to assign
        
        Returns:
            JSON response with the updated member object
        """
        try:
            # Initialize permission service with the current request
            permission_service = PermissionService(request)
            
            # Check if user has permission to update members
            permission_result = permission_service.check_dashboard_owner_permission(dashboard_id)
            if not permission_result.granted:
                return json_error("Only dashboard owners can update member roles", status=403)
            
            # Parse request data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                return json_error(f"Invalid JSON format: {str(e)}", status=400)
            
            # Validate required fields
            if 'role' not in data:
                return json_error("Role is required", status=400)
                
            role = data['role']
            
            # Validate role
            if role not in [DashboardMemberRole.EDITOR, DashboardMemberRole.VIEWER]:
                return json_error(f"Invalid role. Must be one of: {DashboardMemberRole.EDITOR}, {DashboardMemberRole.VIEWER}", status=400)
            
            # Get member and verify it belongs to the dashboard
            member = self.member_service.get_member(member_id)
            if member.dashboard_id != dashboard_id:
                return json_error("Member does not belong to this dashboard", status=404)
            
            # Prevent changing owner's role
            if member.role == DashboardMemberRole.OWNER:
                return json_error("Cannot change the role of the dashboard owner", status=403)
            
            # Update member role
            updated_member = self.member_service.update_member_role(member_id, role)
            
            # Prepare response
            member_data = {
                'id': updated_member.id,
                'user': {
                    'id': updated_member.user.id,
                    'username': updated_member.user.username,
                    'email': updated_member.user.email
                },
                'role': updated_member.role,
                'joined_at': updated_member.joined_at.isoformat()
            }
            
            return json_success(member_data)
            
        except Exception as e:
            return handle_exception(e)
    
    def delete(self, request: HttpRequest, dashboard_id: int, member_id: int) -> HttpResponse:
        """
        Remove a member from a dashboard.
        
        Returns:
            JSON response confirming the deletion
        """
        try:
            # Initialize permission service with the current request
            permission_service = PermissionService(request)
            
            # Check if user has permission to remove members
            permission_result = permission_service.check_dashboard_owner_permission(dashboard_id)
            if not permission_result.granted:
                return json_error("Only dashboard owners can remove members", status=403)
            
            # Get member and verify it belongs to the dashboard
            member = self.member_service.get_member(member_id)
            if member.dashboard_id != dashboard_id:
                return json_error("Member does not belong to this dashboard", status=404)
            
            # Prevent removing dashboard owner
            if member.role == DashboardMemberRole.OWNER:
                return json_error("Cannot remove the dashboard owner", status=403)
            
            # Remove member
            self.member_service.remove_member(member_id)
            
            return json_success({"message": "Member removed successfully"})
            
        except Exception as e:
            return handle_exception(e) 