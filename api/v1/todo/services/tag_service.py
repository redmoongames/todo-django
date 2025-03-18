from typing import Dict, Any
from django.db.models import QuerySet
from django.db import transaction

from ..models.tag import Tag
from ..exceptions import APIError

DEFAULT_COLOR = '#000000'

class TagService:
    def get_tag(self, tag_id: int) -> Tag:
        try:
            return Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            raise APIError("Tag not found", status=404)

    def get_dashboard_tags(self, dashboard_id: int) -> QuerySet[Tag]:
        return Tag.objects.filter(dashboard_id=dashboard_id)

    def create_tag(self, dashboard_id: int, data: Dict[str, Any]) -> Tag:
        name = data.get('name')
        if not name:
            raise APIError("Tag name is required", status=400)
            
        if Tag.objects.filter(dashboard_id=dashboard_id, name=name).exists():
            raise APIError(f"Tag with name '{name}' already exists in this dashboard", status=400)
            
        color = data.get('color', DEFAULT_COLOR)
        try:
            with transaction.atomic():
                tag = Tag.objects.create(dashboard_id=dashboard_id, name=name, color=color)
                return tag
        except Exception as e:
            raise APIError(f"Failed to create tag: {str(e)}", status=500)

    def update_tag(self, tag_id: int, data: Dict[str, Any]) -> Tag:
        tag = self.get_tag(tag_id)
        
        with transaction.atomic():
            for key, value in data.items():
                setattr(tag, key, value)
            tag.save()
            
        return tag

    def delete_tag(self, tag_id: int) -> None:
        tag = self.get_tag(tag_id)
        tag.delete()

    def get_tag_todos(self, tag_id: int) -> QuerySet:
        tag: Tag = self.get_tag(tag_id)
        return tag.todo_set.all() 