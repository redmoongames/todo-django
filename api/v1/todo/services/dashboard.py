from typing import Dict, Any
from django.db.models import QuerySet
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models.dashboard import Dashboard
from ..models.dashboard_member import DashboardMember
from ..exceptions import APIError
from ..constants import DashboardMemberRole

User = get_user_model()

class DashboardService:
    def get_dashboard(self, dashboard_id: int) -> Dashboard:
        try:
            return Dashboard.objects.get(id=dashboard_id)
        except Dashboard.DoesNotExist:
            raise APIError("Dashboard not found", status=404)

    def get_user_dashboards(self, user):
        if hasattr(user, 'id'):
            user_id = user.id
        else:
            user_id = user
        return Dashboard.objects.filter(members__user_id=user_id)

    def create_dashboard(self, user_id: int, data: Dict[str, Any]) -> Dashboard:
        # Debug to see what data we're receiving
        print(f"Service received data: {data}")
        
        # Validate required fields
        if not data.get('title'):
            raise APIError("Dashboard title is required", status=400)
            
        with transaction.atomic():
            try:
                # Create the dashboard - the signal will handle creating the owner member
                dashboard = Dashboard.objects.create(
                    title=data['title'],
                    description=data.get('description', ''),
                    owner_id=user_id,
                    is_public=data.get('is_public', False)
                )
                
                # No need to create DashboardMember here - it's handled by the signal
                print(f"Created dashboard with id {dashboard.id} for user {user_id}")
                
                return dashboard
            except Exception as e:
                # More detailed error information
                print(f"Error creating dashboard: {str(e)}")
                raise

    def update_dashboard(self, dashboard_id: int, data: Dict[str, Any]) -> Dashboard:
        dashboard = self.get_dashboard(dashboard_id)
        
        with transaction.atomic():
            for key, value in data.items():
                setattr(dashboard, key, value)
            dashboard.updated_at = timezone.now()
            dashboard.save()
            
        return dashboard

    def delete_dashboard(self, dashboard_id: int) -> None:
        dashboard = self.get_dashboard(dashboard_id)
        dashboard.delete()

    def get_dashboard_members(self, dashboard_id: int) -> QuerySet[DashboardMember]:
        return DashboardMember.objects.filter(dashboard_id=dashboard_id)

    def add_dashboard_member(
        self,
        dashboard_id: int,
        email: str,
        role: str = DashboardMemberRole.VIEWER
    ) -> DashboardMember:
        dashboard = self.get_dashboard(dashboard_id)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise APIError(f"User with email {email} not found", "user_not_found", 404)
            
        if DashboardMember.objects.filter(dashboard=dashboard, user=user).exists():
            raise APIError(
                f"User {email} already has access to this dashboard",
                "already_member",
                400
            )
            
        with transaction.atomic():
            member = DashboardMember.objects.create(
                dashboard=dashboard,
                user=user,
                role=role
            )
            
        return member

    def update_member_role(
        self,
        dashboard_id: int,
        user_id: int,
        role: str
    ) -> DashboardMember:
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
            
        if member.role == DashboardMemberRole.OWNER:
            raise APIError(
                "Cannot remove dashboard owner",
                "cannot_remove_owner",
                400
            )
            
        member.delete() 