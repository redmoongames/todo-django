from typing import Dict, Any, List
from ..models.tag import Tag
from datetime import datetime


class TagSerializer:
    def serialize(self, tag: Tag) -> Dict[str, Any]:
        data = {
            'id': tag.id,
            'name': tag.name,
            'color': tag.color
        }
        
        if hasattr(tag, 'created_at') and tag.created_at:
            data['created_at'] = tag.created_at.isoformat()
        else:
            data['created_at'] = datetime.now().isoformat()
            
        if hasattr(tag, 'updated_at') and tag.updated_at:
            data['updated_at'] = tag.updated_at.isoformat()
        else:
            data['updated_at'] = datetime.now().isoformat()
            
        return data

    def serialize_many(self, tags: List[Tag]) -> List[Dict[str, Any]]:
        return [self.serialize(tag) for tag in tags] 