
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views import View

from api.v1.todo.utils.responses import json_success, handle_exception
from api.v1.todo.services import TodoService


class TodoDetailView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = TodoService()

    @require_http_methods(["GET"])
    @login_required
    def get(self, request: HttpRequest, dashboard_id: int, todo_id: int) -> HttpResponse:
        try:
            todo = self.service.get_todo(todo_id)
            return json_success(todo.to_dict())
        except Exception as e:
            return handle_exception(e)
    
    @require_http_methods(["PUT"])
    @login_required
    def put(self, request: HttpRequest, dashboard_id: int, todo_id: int) -> HttpResponse:
        try:
            data = request.json()
            todo = self.service.update_todo(todo_id=todo_id, data=data)
            return json_success(todo.to_dict())
        except Exception as e:
            return handle_exception(e)
    
    @require_http_methods(["DELETE"])
    @login_required
    def delete(self, request: HttpRequest, dashboard_id: int, todo_id: int) -> HttpResponse:
        try:
            self.service.delete_todo(todo_id)
            return json_success({"message": "Todo deleted successfully"})
        except Exception as e:
            return handle_exception(e) 