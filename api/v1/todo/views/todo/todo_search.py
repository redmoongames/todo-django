
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views import View

from api.v1.todo.utils.responses import json_success, json_error, handle_exception
from api.v1.todo.services import TodoService
from api.v1.todo.serializers import TodoSerializer


class TodoSearchView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = TodoService()
        self.serializer = TodoSerializer()

    @require_http_methods(["GET"])
    @login_required
    def get(self, request: HttpRequest, dashboard_id: int) -> HttpResponse:
        try:
            query = request.GET.get('q')
            if not query:
                return json_error("Search query is required", status=400)

            status = request.GET.get('status')
            tag_id = request.GET.get('tag_id')

            todos = self.service.search_todos(
                dashboard_id=dashboard_id,
                query=query,
                status=status,
                tag_id=tag_id
            )

            return json_success({
                'todos': self.serializer.serialize_many(todos)
            })
        except Exception as e:
            return handle_exception(e) 