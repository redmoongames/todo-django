from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views import View

from api.v1.todo.utils.responses import json_success, json_error, handle_exception
from api.v1.todo.services import TodoService
from api.v1.todo.serializers import TodoSerializer


class TodoActionView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = TodoService()
        self.serializer = TodoSerializer()

    @require_http_methods(["POST"])
    @login_required
    def post(self, request: HttpRequest, dashboard_id: int, todo_id: int, action: str) -> HttpResponse:
        try:
            if action == 'complete':
                todo = self.service.complete_todo(todo_id=todo_id, user_id=request.user.id)
                return json_success(self.serializer.serialize(todo))
            elif action == 'uncomplete':
                todo = self.service.uncomplete_todo(todo_id=todo_id)
                return json_success(self.serializer.serialize(todo))
            else:
                return json_error("Invalid action", status=400)
        except Exception as e:
            return handle_exception(e)