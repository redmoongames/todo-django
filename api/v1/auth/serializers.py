from typing import Dict, Any, List, Optional
from django.contrib.auth.models import User

from api.v1.todo.models.tag import Tag
from api.v1.todo.models.dashboard import Dashboard
from api.v1.todo.models.dashboard_member import DashboardMember
from api.v1.todo.models.todo import Todo
from api.v1.todo.services.permission_service import PermissionService
from api.v1.todo.serializers import TodoSerializer, TagSerializer, DashboardSerializer


def serialize_user(user: User) -> Dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }


def serialize_tag(tag: Tag) -> Dict[str, Any]:
    return {
        "id": tag.id,
        "name": tag.name,
        "color": tag.color
    }


def serialize_dashboard_member(member: DashboardMember) -> Dict[str, Any]:
    return {
        "id": member.id,
        "user": serialize_user(member.user),
        "role": member.role,
        "joined_at": member.joined_at.isoformat()
    }


def serialize_dashboard(dashboard: Dashboard, user: Optional[User] = None) -> Dict[str, Any]:
    serializer = DashboardSerializer()
    data = serializer.serialize(dashboard)
    
    if user:
        permission_service = PermissionService(None)
        data["role"] = permission_service.get_user_role(user, dashboard)
    
    return data


def serialize_todo(todo: Todo) -> Dict[str, Any]:
    serializer = TodoSerializer()
    return serializer.serialize(todo) 