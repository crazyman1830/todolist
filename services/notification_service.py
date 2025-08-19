"""
알림 관련 기능을 처리하는 서비스

목표 날짜 관련 알림, 상태바 요약 정보, 시작 시 알림 등을 관리합니다.
"""

from typing import List, Dict, TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from models.todo import Todo
    from services.todo_service import TodoService


class NotificationService:
    """알림 관련 기능을 처리하는 서비스"""
    
    def __init__(self, todo_service: 'TodoService'):
        """
        NotificationService 초기화
        
        Args:
            todo_service: TodoService 인스턴스
        """
        self.todo_service = todo_service
    
    def get_overdue_todos(self) -> List['Todo']:
        """
        지연된 할일들 반환
        
        Requirements 8.2: 지연된 할일 개수를 상태바에 표시
        
        Returns:
            List[Todo]: 목표 날짜가 지난 미완료 할일 목록
        """
        return self.todo_service.get_overdue_todos()
    
    def get_due_today_todos(self) -> List['Todo']:
        """
        오늘 마감인 할일들 반환
        
        Requirements 8.1: 오늘 마감인 할일 개수를 상태바에 표시
        
        Returns:
            List[Todo]: 오늘 마감인 미완료 할일 목록
        """
        return self.todo_service.get_due_today_todos()
    
    def get_urgent_todos(self) -> List['Todo']:
        """
        긴급한 할일들 반환 (24시간 이내)
        
        Requirements 8.4: 목표 날짜가 임박한 할일 알림
        
        Returns:
            List[Todo]: 24시간 이내 마감인 미완료 할일 목록
        """
        return self.todo_service.get_urgent_todos(hours=24)
    
    def should_show_startup_notification(self) -> bool:
        """
        시작 시 알림을 표시해야 하는지 확인
        
        Requirements 8.4: 목표 날짜가 임박한 할일이 있으면 시작 시 알림 표시
        
        Returns:
            bool: 알림을 표시해야 하면 True
        """
        # 지연된 할일이나 오늘 마감인 할일이 있으면 알림 표시
        overdue_todos = self.get_overdue_todos()
        due_today_todos = self.get_due_today_todos()
        
        return len(overdue_todos) > 0 or len(due_today_todos) > 0
    
    def get_startup_notification_message(self) -> str:
        """
        시작 시 알림 메시지 생성
        
        Requirements 8.4: 시작 시 알림 다이얼로그 표시
        
        Returns:
            str: 알림 메시지 텍스트
        """
        overdue_todos = self.get_overdue_todos()
        due_today_todos = self.get_due_today_todos()
        
        messages = []
        
        if len(overdue_todos) > 0:
            messages.append(f"⚠️ 지연된 할일이 {len(overdue_todos)}개 있습니다.")
        
        if len(due_today_todos) > 0:
            messages.append(f"📅 오늘 마감인 할일이 {len(due_today_todos)}개 있습니다.")
        
        if not messages:
            return "모든 할일이 정상적으로 관리되고 있습니다."
        
        return "\n".join(messages)
    
    def get_status_bar_summary(self) -> Dict[str, int]:
        """
        상태바에 표시할 요약 정보 반환
        
        Requirements 8.1, 8.2: 상태바에 오늘 마감 및 지연된 할일 개수 표시
        
        Returns:
            Dict[str, int]: 상태바 요약 정보
            - 'overdue': 지연된 할일 개수
            - 'due_today': 오늘 마감인 할일 개수
            - 'urgent': 긴급한 할일 개수 (24시간 이내)
            - 'total': 전체 할일 개수
            - 'completed': 완료된 할일 개수
        """
        all_todos = self.todo_service.get_all_todos()
        overdue_todos = self.get_overdue_todos()
        due_today_todos = self.get_due_today_todos()
        urgent_todos = self.get_urgent_todos()
        
        # 완료된 할일 개수 계산
        completed_todos = [todo for todo in all_todos if todo.is_completed()]
        
        return {
            'overdue': len(overdue_todos),
            'due_today': len(due_today_todos),
            'urgent': len(urgent_todos),
            'total': len(all_todos),
            'completed': len(completed_todos)
        }
    
    def get_detailed_notification_info(self) -> Dict[str, List[str]]:
        """
        상세한 알림 정보 반환 (디버깅 및 상세 표시용)
        
        Returns:
            Dict[str, List[str]]: 카테고리별 할일 제목 목록
        """
        overdue_todos = self.get_overdue_todos()
        due_today_todos = self.get_due_today_todos()
        urgent_todos = self.get_urgent_todos()
        
        return {
            'overdue': [todo.title for todo in overdue_todos],
            'due_today': [todo.title for todo in due_today_todos],
            'urgent': [todo.title for todo in urgent_todos]
        }
    
    def get_notification_priority(self) -> str:
        """
        알림 우선순위 반환
        
        Returns:
            str: 우선순위 레벨 ('high', 'medium', 'low', 'none')
        """
        overdue_count = len(self.get_overdue_todos())
        due_today_count = len(self.get_due_today_todos())
        
        if overdue_count > 0:
            return 'high'
        elif due_today_count > 0:
            return 'medium'
        elif len(self.get_urgent_todos()) > 0:
            return 'low'
        else:
            return 'none'
    
    def format_status_bar_text(self) -> str:
        """
        상태바에 표시할 텍스트 포맷팅
        
        Requirements 8.1, 8.2: 상태바 정보 표시
        
        Returns:
            str: 상태바 텍스트
        """
        summary = self.get_status_bar_summary()
        
        status_parts = []
        
        # 지연된 할일
        if summary['overdue'] > 0:
            status_parts.append(f"지연: {summary['overdue']}개")
        
        # 오늘 마감
        if summary['due_today'] > 0:
            status_parts.append(f"오늘 마감: {summary['due_today']}개")
        
        # 전체 할일 정보
        status_parts.append(f"전체: {summary['total']}개")
        
        # 완료율
        if summary['total'] > 0:
            completion_rate = (summary['completed'] / summary['total']) * 100
            status_parts.append(f"완료율: {completion_rate:.0f}%")
        
        return " | ".join(status_parts)
    
    def get_todos_with_overdue_subtasks(self) -> List['Todo']:
        """
        지연된 하위 작업이 있는 할일들 반환
        
        Requirements 7.3: 하위 작업 지연 상태 관리
        
        Returns:
            List[Todo]: 지연된 하위 작업이 있는 할일 목록
        """
        return self.todo_service.get_todos_with_overdue_subtasks()
    
    def get_notification_summary_for_period(self, days: int = 7) -> Dict[str, int]:
        """
        지정된 기간 동안의 알림 요약 정보 반환
        
        Requirements 8.3: 목표 날짜별 할일 분포 정보
        
        Args:
            days: 조회할 기간 (일 단위, 기본 7일)
            
        Returns:
            Dict[str, int]: 기간별 할일 분포
        """
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        todos_in_period = self.todo_service.get_todos_by_due_date(now, end_date)
        
        # 일별 분포 계산
        daily_distribution = {}
        for i in range(days + 1):
            target_date = now + timedelta(days=i)
            date_key = target_date.strftime("%Y-%m-%d")
            
            daily_count = 0
            for todo in todos_in_period:
                if (todo.due_date and 
                    todo.due_date.date() == target_date.date() and
                    not todo.is_completed()):
                    daily_count += 1
            
            daily_distribution[date_key] = daily_count
        
        return daily_distribution