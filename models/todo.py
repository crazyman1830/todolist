from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from .subtask import SubTask


@dataclass
class Todo:
    """할일 데이터 모델 클래스"""
    id: int
    title: str
    created_at: datetime
    folder_path: str
    subtasks: List['SubTask'] = field(default_factory=list)
    is_expanded: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Todo 객체를 딕셔너리로 직렬화"""
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'folder_path': self.folder_path,
            'subtasks': [subtask.to_dict() for subtask in self.subtasks],
            'is_expanded': self.is_expanded
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Todo':
        """딕셔너리에서 Todo 객체로 역직렬화"""
        from .subtask import SubTask
        
        subtasks = []
        if 'subtasks' in data:
            subtasks = [SubTask.from_dict(subtask_data) for subtask_data in data['subtasks']]
        
        return cls(
            id=data['id'],
            title=data['title'],
            created_at=datetime.fromisoformat(data['created_at']),
            folder_path=data['folder_path'],
            subtasks=subtasks,
            is_expanded=data.get('is_expanded', True)
        )
    
    def get_folder_name(self) -> str:
        """할일 폴더명 생성"""
        # 특수문자를 언더스코어로 대체하고 최대 길이 제한
        sanitized_title = re.sub(r'[^\w\s-]', '_', self.title)
        sanitized_title = re.sub(r'[-\s]+', '_', sanitized_title)
        sanitized_title = sanitized_title.strip('_')[:30]  # 최대 30자로 제한
        
        return f"todo_{self.id}_{sanitized_title}"
    
    def get_completion_rate(self) -> float:
        """하위 작업들의 완료율을 계산하여 반환 (0.0 ~ 1.0)"""
        if not self.subtasks:
            return 0.0
        
        completed_count = sum(1 for subtask in self.subtasks if subtask.is_completed)
        return completed_count / len(self.subtasks)
    
    def is_completed(self) -> bool:
        """모든 하위 작업이 완료되었는지 확인"""
        if not self.subtasks:
            return False
        
        return all(subtask.is_completed for subtask in self.subtasks)
    
    def add_subtask(self, subtask: 'SubTask') -> None:
        """하위 작업을 추가"""
        if subtask.todo_id != self.id:
            raise ValueError(f"SubTask todo_id ({subtask.todo_id}) does not match Todo id ({self.id})")
        
        # 중복 ID 체크
        existing_ids = {st.id for st in self.subtasks}
        if subtask.id in existing_ids:
            raise ValueError(f"SubTask with id {subtask.id} already exists")
        
        self.subtasks.append(subtask)
    
    def remove_subtask(self, subtask_id: int) -> bool:
        """하위 작업을 제거. 성공하면 True, 실패하면 False 반환"""
        for i, subtask in enumerate(self.subtasks):
            if subtask.id == subtask_id:
                del self.subtasks[i]
                return True
        return False