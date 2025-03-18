from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models.dashboard_member import DashboardMember
from ..exceptions import APIError
from ..constants import DashboardMemberRole
from .permission_service import PermissionService

User = get_user_model()

class MemberService:
    def __init__(self):
        self.permission_service = PermissionService(None)

    def get_member(self, member_id: int) -> DashboardMember:
        """
        Retrieves a dashboard member by ID.
        
        Args:
            member_id: ID of the member to retrieve
            
        Returns:
            DashboardMember object
            
        Raises:
            APIError: If member not found
        """
        try:
            return DashboardMember.objects.get(id=member_id)
        except DashboardMember.DoesNotExist:
            raise APIError("Member not found", status=404)

    def get_dashboard_members(self, dashboard_id: int) -> QuerySet[DashboardMember]:
        """
        Retrieves all members of a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard
            
        Returns:
            QuerySet of DashboardMember objects
        """
        return DashboardMember.objects.filter(dashboard_id=dashboard_id)

    def get_user_memberships(self, user_id: int) -> QuerySet[DashboardMember]:
        """
        Retrieves all dashboard memberships of a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            QuerySet of DashboardMember objects
        """
        return DashboardMember.objects.filter(user_id=user_id)

    def add_member(
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
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise APIError(f"User with email {email} not found", "user_not_found", 404)
            
        if DashboardMember.objects.filter(dashboard_id=dashboard_id, user=user).exists():
            raise APIError(
                f"User {email} already has access to this dashboard",
                "already_member",
                400
            )
            
        with transaction.atomic():
            member = DashboardMember.objects.create(
                dashboard_id=dashboard_id,
                user=user,
                role=role
            )
            
        return member

    def update_member_role(self, member_id: int, role: str) -> DashboardMember:
        """
        Updates the role of a dashboard member.
        
        Args:
            member_id: ID of the member
            role: New role to assign
            
        Returns:
            Updated DashboardMember object
        """
        member = self.get_member(member_id)
        
        with transaction.atomic():
            member.role = role
            member.save()
            
        return member

    def remove_member(self, member_id: int) -> None:
        """
        Removes a member from a dashboard.
        
        Args:
            member_id: ID of the member to remove
        """
        member = self.get_member(member_id)
        member.delete()

    def is_owner(self, dashboard_id: int, user_id: int) -> bool:
        """
        Checks if a user is the owner of a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard
            user_id: ID of the user
            
        Returns:
            True if user is the owner, False otherwise
        """
        return self.permission_service.is_dashboard_owner(dashboard_id, user_id)

    def is_editor(self, dashboard_id: int, user_id: int) -> bool:
        """
        Checks if a user is an editor or owner of a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard
            user_id: ID of the user
            
        Returns:
            True if user is an editor or owner, False otherwise
        """
        return self.permission_service.is_dashboard_editor(dashboard_id, user_id) 