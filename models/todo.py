from dataclasses import dataclass, field
from datetime import datetime, timedelta
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
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Todo 객체를 딕셔너리로 직렬화"""
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'folder_path': self.folder_path,
            'subtasks': [subtask.to_dict() for subtask in self.subtasks],
            'is_expanded': self.is_expanded,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Todo':
        """딕셔너리에서 Todo 객체로 역직렬화"""
        from .subtask import SubTask
        
        subtasks = []
        if 'subtasks' in data:
            subtasks = [SubTask.from_dict(subtask_data) for subtask_data in data['subtasks']]
        
        # 새로운 필드들에 대한 마이그레이션 로직 (기존 데이터 호환성)
        due_date = None
        if 'due_date' in data and data['due_date']:
            due_date = datetime.fromisoformat(data['due_date'])
        
        completed_at = None
        if 'completed_at' in data and data['completed_at']:
            completed_at = datetime.fromisoformat(data['completed_at'])
        
        return cls(
            id=data['id'],
            title=data['title'],
            created_at=datetime.fromisoformat(data['created_at']),
            folder_path=data['folder_path'],
            subtasks=subtasks,
            is_expanded=data.get('is_expanded', True),
            due_date=due_date,
            completed_at=completed_at
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
        """할일이 완료되었는지 확인"""
        # completed_at이 설정되어 있으면 완료된 것으로 간주
        if self.completed_at is not None:
            return True
        
        # 하위 작업이 있는 경우 모든 하위 작업이 완료되었는지 확인
        if self.subtasks:
            return all(subtask.is_completed for subtask in self.subtasks)
        
        # 하위 작업이 없고 completed_at도 없으면 미완료
        return False
    
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
    
    # 목표 날짜 관련 메서드들
    def set_due_date(self, due_date: Optional[datetime]) -> None:
        """
        할일의 목표 날짜 설정
        
        Requirements 1.1, 1.2: 목표 완료 날짜/시간 설정 기능
        
        Args:
            due_date: 설정할 목표 날짜 (None이면 목표 날짜 제거)
        """
        self.due_date = due_date
    
    def get_due_date(self) -> Optional[datetime]:
        """
        할일의 목표 날짜 반환
        
        Returns:
            Optional[datetime]: 목표 날짜 (설정되지 않았으면 None)
        """
        return self.due_date
    
    def is_overdue(self) -> bool:
        """
        할일이 지연되었는지 확인
        
        Requirements 3.1: 목표 날짜가 지난 할일 시각적 구분
        
        Returns:
            bool: 목표 날짜가 지났고 완료되지 않았으면 True
        """
        if self.due_date is None or self.is_completed():
            return False
        
        return datetime.now() > self.due_date
    
    def get_urgency_level(self) -> str:
        """
        할일의 긴급도 레벨 반환
        
        Requirements 3.1, 3.2, 3.3: 목표 날짜 기준 시각적 구분
        
        Returns:
            str: 긴급도 레벨 ('overdue', 'urgent', 'warning', 'normal')
        """
        from services.date_service import DateService
        
        # 완료된 할일은 normal로 처리
        if self.is_completed():
            return 'normal'
        
        return DateService.get_urgency_level(self.due_date)
    
    def get_time_remaining_text(self) -> str:
        """
        남은 시간을 사용자 친화적 텍스트로 반환
        
        Requirements 5.1, 5.2, 5.3, 5.4: 남은 시간 직관적 표시
        
        Returns:
            str: 시간 표시 텍스트 ("D-3", "3시간 후", "완료: 01/08 16:30" 등)
        """
        from services.date_service import DateService
        
        return DateService.get_time_remaining_text(self.due_date, self.completed_at)
    
    def mark_completed(self) -> None:
        """
        할일을 완료로 표시
        
        모든 하위 작업을 완료 상태로 변경하고 완료 시간을 기록합니다.
        
        Requirements 3.4: 완료 시 긴급도 색상 제거 및 완료 표시
        """
        # 모든 하위 작업을 완료로 표시
        for subtask in self.subtasks:
            if not subtask.is_completed:
                subtask.is_completed = True
                subtask.completed_at = datetime.now()
        
        # 할일 완료 시간 기록
        self.completed_at = datetime.now()
    
    def mark_uncompleted(self) -> None:
        """
        할일을 미완료로 표시
        
        완료 시간을 제거하고 하위 작업들도 미완료 상태로 변경할 수 있습니다.
        """
        self.completed_at = None
        
        # 모든 하위 작업도 미완료로 변경
        for subtask in self.subtasks:
            subtask.is_completed = False
            subtask.completed_at = None
    
    def has_overdue_subtasks(self) -> bool:
        """
        지연된 하위 작업이 있는지 확인
        
        Requirements 7.3: 하위 작업 목표 날짜 관리
        
        Returns:
            bool: 지연된 하위 작업이 있으면 True
        """
        now = datetime.now()
        for subtask in self.subtasks:
            if (not subtask.is_completed and 
                subtask.due_date is not None and 
                subtask.due_date < now):
                return True
        return False
    
    def validate_subtask_due_date(self, subtask_due_date: datetime) -> tuple[bool, str]:
        """
        하위 작업의 목표 날짜 유효성 검사
        
        Requirements 7.2: 하위 작업 목표 날짜가 상위 할일보다 늦은 경우 경고
        
        Args:
            subtask_due_date: 검사할 하위 작업의 목표 날짜
            
        Returns:
            tuple[bool, str]: (유효성 여부, 오류 메시지)
        """
        from services.date_service import DateService
        
        return DateService.validate_due_date(subtask_due_date, self.due_date)
    
    def get_time_remaining(self) -> Optional[timedelta]:
        """
        목표 날짜까지 남은 시간 반환
        
        Returns:
            Optional[timedelta]: 남은 시간 (목표 날짜가 없으면 None)
        """
        if self.due_date is None:
            return None
        
        return self.due_date - datetime.now()