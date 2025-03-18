from typing import Dict, Any, List
from ..models.dashboard import Dashboard


class DashboardSerializer:
    def serialize(self, dashboard: Dashboard) -> Dict[str, Any]:
        return {
            'id': dashboard.id,
            'title': dashboard.title,
            'description': dashboard.description,
            'created_at': dashboard.created_at.isoformat(),
            'is_public': dashboard.is_public,
            'owner_id': dashboard.owner_id,
            'members': [member.id for member in dashboard.members.all()]
        }

    def serialize_many(self, dashboards: List[Dashboard]) -> List[Dict[str, Any]]:
        return [self.serialize(dashboard) for dashboard in dashboards] 