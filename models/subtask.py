from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class SubTask:
    """하위 작업 데이터 모델 클래스"""
    id: int
    todo_id: int
    title: str
    is_completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """SubTask 객체를 딕셔너리로 직렬화"""
        return {
            'id': self.id,
            'todo_id': self.todo_id,
            'title': self.title,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubTask':
        """딕셔너리에서 SubTask 객체로 역직렬화"""
        return cls(
            id=data['id'],
            todo_id=data['todo_id'],
            title=data['title'],
            is_completed=data['is_completed'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
    
    def toggle_completion(self) -> None:
        """완료 상태를 토글"""
        self.is_completed = not self.is_completed