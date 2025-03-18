from typing import Dict, Any, Union, List, Optional, TypeVar, cast, TYPE_CHECKING
from django.db.models import QuerySet
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserType
import logging

from ..models.dashboard import Dashboard
from ..models.dashboard_member import DashboardMember
from ..exceptions import APIError
from ..constants import DashboardMemberRole

User = get_user_model()
UserType = TypeVar('UserType', bound=User)
logger = logging.getLogger(__name__)

class DashboardService:
    def get_dashboard(self, dashboard_id: int) -> Dashboard:
        """
        Retrieves a dashboard by its ID.
        
        Args:
            dashboard_id: The ID of the dashboard to retrieve
            
        Returns:
            Dashboard object
            
        Raises:
            APIError: If dashboard not found with 404 status
        """
        try:
            return Dashboard.objects.get(id=dashboard_id)
        except Dashboard.DoesNotExist:
            raise APIError("Dashboard not found", status=404)

    def get_user_dashboards_by_id(self, user_id: int) -> QuerySet[Dashboard]:
        """
        Returns all dashboards where the user with the specified ID is a member.
        
        Args:
            user_id: ID of the user
            
        Returns:
            QuerySet of Dashboard objects the user has access to.
            Returns an empty QuerySet if the user doesn't exist or has no dashboards.
            This preserves RESTful behavior and information security by not revealing 
            whether a user ID exists.
        """
        return Dashboard.objects.filter(members__user_id=user_id)
        
    def get_user_dashboards(self, user: UserType) -> QuerySet[Dashboard]:
        """
        Returns all dashboards where the given user is a member.
        
        Args:
            user: User object
            
        Returns:
            QuerySet of Dashboard objects the user has access to
            
        Raises:
            APIError: If the provided user object is None or invalid
        """
        if user is None:
            raise APIError("User object cannot be None", status=400)
            
        if not hasattr(user, 'id'):
            raise APIError("Invalid user object provided", status=400)
            
        return self.get_user_dashboards_by_id(user.id)

    def create_dashboard(self, user_id: int, data: Dict[str, Any]) -> Dashboard:
        """
        Creates a new dashboard owned by the specified user.
        
        Args:
            user_id: ID of the user who will own the dashboard
            data: Dictionary containing dashboard data (title, description, is_public)
            
        Returns:
            Newly created Dashboard object
            
        Raises:
            APIError: If title is missing, user not found, or creation fails
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise APIError(f"User with ID {user_id} not found", status=404)
        title = data.get('title')
        if not title:
            raise APIError("Dashboard title is required", status=400)
        description = data.get('description', '')
        is_public = data.get('is_public', False)
        with transaction.atomic():
            try:
                dashboard = Dashboard.objects.create(
                    title=title, 
                    description=description, 
                    owner_id=user_id, 
                    is_public=is_public
                )
                # The Dashboard model's post_save signal automatically creates 
                # a DashboardMember for the owner, so we don't need to do it here
                return dashboard
            except Exception as e:
                raise APIError(f"Failed to create dashboard: {str(e)}", status=500)

    def update_dashboard(self, dashboard_id: int, data: Dict[str, Any]) -> Dashboard:
        """
        Updates an existing dashboard with the provided data.
        
        Args:
            dashboard_id: ID of the dashboard to update
            data: Dictionary containing fields to update
            
        Returns:
            Updated Dashboard object
            
        Raises:
            APIError: If dashboard title is empty
        """
        dashboard = self.get_dashboard(dashboard_id)
        allowed_fields = {'title', 'description', 'is_public'}
        
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            logger.warning(f"Invalid fields provided when updating dashboard {dashboard_id}: {', '.join(invalid_fields)}")
            
        valid_data = {}
        for key, value in data.items():
            if key in allowed_fields:
                valid_data[key] = value
        
        if 'title' in valid_data and not valid_data['title']:
            raise APIError("Dashboard title cannot be empty", status=400)
            
        with transaction.atomic():
            for key, value in valid_data.items():
                setattr(dashboard, key, value)
            dashboard.updated_at = timezone.now()
            dashboard.save()
            
        return dashboard

    def delete_dashboard(self, dashboard_id: int) -> None:
        """
        Deletes a dashboard by its ID.
        
        Args:
            dashboard_id: ID of the dashboard to delete
        """
        dashboard = self.get_dashboard(dashboard_id)
        dashboard.delete()

    def get_dashboard_members(self, dashboard_id: int) -> QuerySet[DashboardMember]:
        """
        Retrieves all members of a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard
            
        Returns:
            QuerySet of DashboardMember objects
        """
        return DashboardMember.objects.filter(dashboard_id=dashboard_id)

    def add_dashboard_member(
        self,
        dashboard_id: int,
        email: str,
        role: str = DashboardMemberRole.VIEWER
    ) -> DashboardMember:
        """
        Adds a user as a member to a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard
            email: Email of the user to add
            role: Member role (default: VIEWER)
            
        Returns:
            Created DashboardMember object
            
        Raises:
            APIError: If user not found or is already a member
        """
        dashboard = self.get_dashboard(dashboard_id)
        user = None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise APIError(f"User with email {email} not found", "user_not_found", 404) 
            
        if DashboardMember.objects.filter(dashboard=dashboard, user=user).exists():
            raise APIError(f"User {email} already has access to this dashboard", 400)
            
        try:
            with transaction.atomic():
                member = DashboardMember.objects.create(dashboard=dashboard, user=user, role=role)
        except Exception as e:
            raise APIError(f"Failed to add user {email} to dashboard {dashboard_id}: {str(e)}", 500)
        
        return member

    def update_member_role(
        self,
        dashboard_id: int,
        user_id: int,
        role: str
    ) -> DashboardMember:
        """
        Updates the role of a dashboard member.
        
        Args:
            dashboard_id: ID of the dashboard
            user_id: ID of the user whose role to update
            role: New role to assign
            
        Returns:
            Updated DashboardMember object
            
        Raises:
            APIError: If user is not a member of the dashboard
        """
        try:
            member = DashboardMember.objects.get(
                dashboard_id=dashboard_id,
                user_id=user_id
            )
        except DashboardMember.DoesNotExist:
            raise APIError(
                f"User is not a member of this dashboard",
                "not_member",
                404
            )
            
        with transaction.atomic():
            member.role = role
            member.save()
            
        return member

    def remove_dashboard_member(
        self,
        dashboard_id: int,
        user_id: int
    ) -> None:
        """
        Removes a user from a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard
            user_id: ID of the user to remove
            
        Raises:
            APIError: If dashboard not found, user is not a member, or user is the owner
        """
        # Verify dashboard exists
        try:
            dashboard = Dashboard.objects.get(id=dashboard_id)
        except Dashboard.DoesNotExist:
            raise APIError(f"Dashboard with ID {dashboard_id} not found", status=404)
            
        # Get the member to remove
        try:
            member = DashboardMember.objects.get(
                dashboard_id=dashboard_id,
                user_id=user_id
            )
        except DashboardMember.DoesNotExist:
            raise APIError(
                f"User is not a member of this dashboard",
                "not_member",
                404
            )
            
        # Cannot remove the owner
        if member.role == DashboardMemberRole.OWNER:
            raise APIError(
                "Cannot remove dashboard owner",
                "cannot_remove_owner",
                400
            )
            
        member.delete()
        