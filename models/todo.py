from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
import re


@dataclass
class Todo:
    """할일 데이터 모델 클래스"""
    id: int
    title: str
    created_at: datetime
    folder_path: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Todo 객체를 딕셔너리로 직렬화"""
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'folder_path': self.folder_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Todo':
        """딕셔너리에서 Todo 객체로 역직렬화"""
        return cls(
            id=data['id'],
            title=data['title'],
            created_at=datetime.fromisoformat(data['created_at']),
            folder_path=data['folder_path']
        )
    
    def get_folder_name(self) -> str:
        """할일 폴더명 생성"""
        # 특수문자를 언더스코어로 대체하고 최대 길이 제한
        sanitized_title = re.sub(r'[^\w\s-]', '_', self.title)
        sanitized_title = re.sub(r'[-\s]+', '_', sanitized_title)
        sanitized_title = sanitized_title.strip('_')[:30]  # 최대 30자로 제한
        
        return f"todo_{self.id}_{sanitized_title}"