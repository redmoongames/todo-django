from typing import Dict, Any, List
from ..models.todo import Todo


class TodoSerializer:
    def serialize(self, todo: Todo) -> Dict[str, Any]:
        return {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'due_date': todo.due_date.isoformat() if todo.due_date else None,
            'priority': todo.priority,
            'status': todo.status,
            'tags': [tag.id for tag in todo.tags.all()],
            'created_at': todo.created_at.isoformat(),
            'completed_by': todo.completed_by.id if todo.completed_by else None,
            'completed_at': todo.completed_at.isoformat() if todo.completed_at else None
        }

    def serialize_many(self, todos: List[Todo]) -> List[Dict[str, Any]]:
        return [self.serialize(todo) for todo in todos] 