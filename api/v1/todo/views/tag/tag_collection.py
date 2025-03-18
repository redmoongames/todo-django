from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
import json

from api.v1.todo.utils.responses import json_success, json_error, handle_exception
from api.v1.todo.services import TagService, PermissionService
from api.v1.todo.serializers import TagSerializer
from api.v1.todo.exceptions import APIError

@method_decorator(login_required, name='dispatch')
class TagCollectionView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_service = TagService()
        self.tag_serializer = TagSerializer()

    def get(self, request, dashboard_id: int) -> JsonResponse:
        try:
            permission_service = PermissionService(request)
            permission_service.validate_dashboard_access(dashboard_id)

            tags = self.tag_service.get_dashboard_tags(dashboard_id)
            serialized_data = self.tag_serializer.serialize_many(tags)
            return json_success({"tags": serialized_data})
        except APIError as e:
            return json_error(e.message, status=e.status)
        except Exception as e:
            return json_error(f"Failed to retrieve tags: {str(e)}", status=500)

    def post(self, request, dashboard_id: int) -> JsonResponse:
        try:
            permission_service = PermissionService(request)
            permission_service.validate_dashboard_edit_permission(dashboard_id)

            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
                
            tag = self.tag_service.create_tag(dashboard_id, data)
            serialized_data = self.tag_serializer.serialize(tag)
            return json_success({"tag": serialized_data})
        except json.JSONDecodeError:
            return json_error("Invalid JSON format", status=400)
        except APIError as e:
            return json_error(e.message, status=e.status)
        except Exception as e:
            return handle_exception(e) 