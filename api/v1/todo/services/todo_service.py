from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.db import transaction
from django.utils import timezone
from ..models.todo import Todo
from ..exceptions import APIError


class TodoService:
    def get_todo(self, todo_id: int) -> Todo:
        try:
            return Todo.objects.get(id=todo_id)
        except Todo.DoesNotExist:
            raise APIError("Todo not found", status=404)

    def get_dashboard_todos(
        self, 
        dashboard_id: int, 
        status: Optional[str] = None,
        tag_id: Optional[int] = None,
        sort_by: Optional[str] = None
    ) -> QuerySet[Todo]:
        todos = Todo.objects.filter(dashboard_id=dashboard_id)
        
        if status:
            todos = todos.filter(status=status)
        if tag_id:
            todos = todos.filter(tags__id=tag_id)
            
        if sort_by:
            todos = todos.order_by(sort_by)
            
        return todos

    def create_todo(self, dashboard_id: int, data: Dict[str, Any]) -> Todo:
        with transaction.atomic():
            todo = Todo.objects.create(
                dashboard_id=dashboard_id,
                title=data['title'],
                description=data.get('description', ''),
                due_date=data.get('due_date'),
                priority=data.get('priority', 3),
                status='pending'
            )
            
            if 'tags' in data:
                todo.tags.set(data['tags'])
                
            return todo

    def update_todo(self, todo_id: int, data: Dict[str, Any]) -> Todo:
        todo = self.get_todo(todo_id)
        
        with transaction.atomic():
            for key, value in data.items():
                if key == 'tags':
                    todo.tags.set(value)
                else:
                    setattr(todo, key, value)
            todo.save()
            
        return todo

    def delete_todo(self, todo_id: int) -> None:
        todo = self.get_todo(todo_id)
        todo.delete()

    def complete_todo(self, todo_id: int, user_id: int) -> Todo:
        todo = self.get_todo(todo_id)
        if todo.status == 'completed':
            raise APIError("Todo is already completed", status=400)
            
        todo.complete(user_id)
        return todo

    def uncomplete_todo(self, todo_id: int) -> Todo:
        todo = self.get_todo(todo_id)
        if todo.status == 'pending':
            raise APIError("Todo is already pending", status=400)
            
        todo.uncomplete()
        return todo

    def search_todos(
        self,
        dashboard_id: int,
        query: str,
        status: Optional[str] = None,
        tag_id: Optional[int] = None
    ) -> QuerySet[Todo]:
        todos = Todo.objects.filter(
            dashboard_id=dashboard_id,
            title__icontains=query
        )
        
        if status:
            todos = todos.filter(status=status)
        if tag_id:
            todos = todos.filter(tags__id=tag_id)
            
        return todos 