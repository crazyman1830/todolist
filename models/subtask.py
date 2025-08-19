from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


@dataclass
class SubTask:
    """하위 작업 데이터 모델 클래스"""
    id: int
    todo_id: int
    title: str
    is_completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """SubTask 객체를 딕셔너리로 직렬화"""
        return {
            'id': self.id,
            'todo_id': self.todo_id,
            'title': self.title,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubTask':
        """딕셔너리에서 SubTask 객체로 역직렬화"""
        # 새로운 필드들에 대한 마이그레이션 로직 (기존 데이터 호환성)
        due_date = None
        if 'due_date' in data and data['due_date']:
            due_date = datetime.fromisoformat(data['due_date'])
        
        completed_at = None
        if 'completed_at' in data and data['completed_at']:
            completed_at = datetime.fromisoformat(data['completed_at'])
        
        return cls(
            id=data['id'],
            todo_id=data['todo_id'],
            title=data['title'],
            is_completed=data['is_completed'],
            created_at=datetime.fromisoformat(data['created_at']),
            due_date=due_date,
            completed_at=completed_at
        )
    
    def toggle_completion(self) -> None:
        """완료 상태를 토글하고 completed_at 필드 업데이트"""
        self.is_completed = not self.is_completed
        if self.is_completed:
            self.completed_at = datetime.now()
        else:
            self.completed_at = None
    
    def set_due_date(self, due_date: Optional[datetime]) -> None:
        """
        목표 날짜 설정
        
        Requirements 7.1: 하위 작업에 목표 날짜 설정
        
        Args:
            due_date: 설정할 목표 날짜 (None이면 목표 날짜 제거)
        """
        self.due_date = due_date
    
    def get_due_date(self) -> Optional[datetime]:
        """
        목표 날짜 반환
        
        Returns:
            Optional[datetime]: 설정된 목표 날짜
        """
        return self.due_date
    
    def is_overdue(self) -> bool:
        """
        목표 날짜가 지났는지 확인
        
        Requirements 7.4: 하위 작업 긴급도 표시
        
        Returns:
            bool: 목표 날짜가 지났고 미완료 상태이면 True
        """
        if self.due_date is None or self.is_completed:
            return False
        
        return datetime.now() > self.due_date
    
    def get_urgency_level(self) -> str:
        """
        긴급도 레벨 반환
        
        Requirements 7.4: 하위 작업 긴급도에 따른 색상 표시
        
        Returns:
            str: 긴급도 레벨 ('overdue', 'urgent', 'warning', 'normal')
        """
        # 완료된 작업은 긴급도 없음
        if self.is_completed:
            return 'normal'
        
        # DateService를 사용하여 긴급도 계산
        from services.date_service import DateService
        return DateService.get_urgency_level(self.due_date)
    
    def get_time_remaining(self) -> Optional[timedelta]:
        """
        목표 날짜까지 남은 시간 반환
        
        Returns:
            Optional[timedelta]: 남은 시간 (목표 날짜가 없으면 None)
        """
        if self.due_date is None:
            return None
        
        return self.due_date - datetime.now()
    
    def get_time_remaining_text(self) -> str:
        """
        남은 시간을 사용자 친화적 텍스트로 반환
        
        Requirements 5.4: 하위 작업 시간 표시
        
        Returns:
            str: 시간 표시 텍스트 ("D-3", "3시간 후", "2일 지남" 등)
        """
        # DateService를 사용하여 시간 텍스트 생성
        from services.date_service import DateService
        return DateService.get_time_remaining_text(self.due_date, self.completed_at)
    
    def mark_completed(self) -> None:
        """
        작업을 완료 상태로 변경하고 완료 시간 기록
        
        Requirements 7.4: 완료 상태 변경 시 completed_at 필드 업데이트
        """
        self.is_completed = True
        self.completed_at = datetime.now()
    
    def mark_uncompleted(self) -> None:
        """
        작업을 미완료 상태로 변경하고 완료 시간 제거
        
        Requirements 7.4: 완료 상태 변경 시 completed_at 필드 업데이트
        """
        self.is_completed = False
        self.completed_at = None