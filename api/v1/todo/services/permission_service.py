from typing import NamedTuple, Optional, Tuple
from django.contrib.auth.models import User
from django.http import HttpRequest

from ..models.dashboard import Dashboard
from ..models.dashboard_member import DashboardMember
from ..exceptions import APIError
from ..constants import DashboardMemberRole


class PermissionResult(NamedTuple):
    granted: bool
    message: str


class PermissionService:
    def __init__(self, request: Optional[HttpRequest] = None):
        self.request = request
        self.user = request.user if request else None

    def check_dashboard_access(self, dashboard_id: int) -> PermissionResult:
        """
        Checks if the user has access to view a dashboard.
        Access is granted if dashboard is public or user is a member.
        
        Args:
            dashboard_id: ID of the dashboard to check
            
        Returns:
            PermissionResult with granted status and message
        """
        if not self.request or not self.user:
            return PermissionResult(False, "Authentication required")
            
        try:
            dashboard = Dashboard.objects.get(id=dashboard_id)
            if dashboard.is_public:
                return PermissionResult(True, "Access granted")
                
            member = DashboardMember.objects.get(
                dashboard=dashboard,
                user=self.user
            )
            return PermissionResult(True, "Access granted")
        except Dashboard.DoesNotExist:
            return PermissionResult(False, "Dashboard not found")
        except DashboardMember.DoesNotExist:
            return PermissionResult(False, "Access denied")
    
    def check_dashboard_edit_permission(self, dashboard_id: int) -> PermissionResult:
        """
        Checks if the user has permission to edit a dashboard.
        Edit permission is granted if user is an owner or editor.
        
        Args:
            dashboard_id: ID of the dashboard to check
            
        Returns:
            PermissionResult with granted status and message
        """
        if not self.request or not self.user:
            return PermissionResult(False, "Authentication required")
            
        try:
            dashboard = Dashboard.objects.get(id=dashboard_id)
            member = DashboardMember.objects.get(
                dashboard=dashboard,
                user=self.user
            )
            
            if member.role in [DashboardMemberRole.OWNER, DashboardMemberRole.EDITOR]:
                return PermissionResult(True, "Edit permission granted")
            return PermissionResult(False, "Edit permission denied")
        except Dashboard.DoesNotExist:
            return PermissionResult(False, "Dashboard not found")
        except DashboardMember.DoesNotExist:
            return PermissionResult(False, "Access denied")
    
    def check_dashboard_owner_permission(self, dashboard_id: int) -> PermissionResult:
        """
        Checks if the user is the owner of a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard to check
            
        Returns:
            PermissionResult with granted status and message
        """
        if not self.request or not self.user:
            return PermissionResult(False, "Authentication required")
            
        try:
            dashboard = Dashboard.objects.get(pk=dashboard_id)
        except Dashboard.DoesNotExist:
            return PermissionResult(False, "Dashboard not found")
        
        if not self.user.is_authenticated:
            return PermissionResult(False, "Authentication required")
        
        if dashboard.owner == self.user:
            return PermissionResult(True, "Access granted")
        else:
            return PermissionResult(False, "Only the owner can perform this action")
            
    def validate_dashboard_access(self, dashboard_id: int) -> Dashboard:
        """
        Validates dashboard access and returns the dashboard if access is granted.
        Raises APIError if access is denied.
        
        Args:
            dashboard_id: ID of the dashboard to check
            
        Returns:
            Dashboard object if access is granted
            
        Raises:
            APIError: If access is denied
        """
        result = self.check_dashboard_access(dashboard_id)
        if not result.granted:
            raise APIError(result.message, status=403)
            
        try:
            return Dashboard.objects.get(id=dashboard_id)
        except Dashboard.DoesNotExist:
            raise APIError("Dashboard not found", status=404)
            
    def validate_dashboard_edit_permission(self, dashboard_id: int) -> Dashboard:
        """
        Validates dashboard edit permission and returns the dashboard if permission is granted.
        Raises APIError if permission is denied.
        
        Args:
            dashboard_id: ID of the dashboard to check
            
        Returns:
            Dashboard object if edit permission is granted
            
        Raises:
            APIError: If edit permission is denied
        """
        result = self.check_dashboard_edit_permission(dashboard_id)
        if not result.granted:
            raise APIError(result.message, status=403)
            
        try:
            return Dashboard.objects.get(id=dashboard_id)
        except Dashboard.DoesNotExist:
            raise APIError("Dashboard not found", status=404)
            
    def validate_dashboard_owner_permission(self, dashboard_id: int) -> Dashboard:
        """
        Validates dashboard owner permission and returns the dashboard if user is the owner.
        Raises APIError if user is not the owner.
        
        Args:
            dashboard_id: ID of the dashboard to check
            
        Returns:
            Dashboard object if user is the owner
            
        Raises:
            APIError: If user is not the owner
        """
        result = self.check_dashboard_owner_permission(dashboard_id)
        if not result.granted:
            raise APIError(result.message, status=403)
            
        try:
            return Dashboard.objects.get(id=dashboard_id)
        except Dashboard.DoesNotExist:
            raise APIError("Dashboard not found", status=404)
    
    def get_user_role(self, user: User, dashboard: Dashboard) -> Optional[str]:
        """
        Gets the role of a user in a dashboard.
        
        Args:
            user: User object
            dashboard: Dashboard object
            
        Returns:
            Role of the user or None if user is not a member
        """
        try:
            membership = DashboardMember.objects.get(dashboard=dashboard, user=user)
            return membership.role
        except DashboardMember.DoesNotExist:
            return None
            
    def check_user_role(self, dashboard_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Checks the role of a user in a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard
            user_id: ID of the user
            
        Returns:
            Tuple of (is_member, role) where role is None if user is not a member
        """
        try:
            dashboard = Dashboard.objects.get(id=dashboard_id)
            user = User.objects.get(id=user_id)
            role = self.get_user_role(user, dashboard)
            return (role is not None, role)
        except (Dashboard.DoesNotExist, User.DoesNotExist):
            return (False, None)
            
    def is_dashboard_owner(self, dashboard_id: int, user_id: int) -> bool:
        """
        Checks if a user is the owner of a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard
            user_id: ID of the user
            
        Returns:
            True if user is the owner, False otherwise
        """
        is_member, role = self.check_user_role(dashboard_id, user_id)
        return is_member and role == DashboardMemberRole.OWNER
        
    def is_dashboard_editor(self, dashboard_id: int, user_id: int) -> bool:
        """
        Checks if a user is an editor or owner of a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard
            user_id: ID of the user
            
        Returns:
            True if user is an editor or owner, False otherwise
        """
        is_member, role = self.check_user_role(dashboard_id, user_id)
        return is_member and role in [DashboardMemberRole.OWNER, DashboardMemberRole.EDITOR] 