"""
NotificationService 테스트

알림 서비스의 기능들을 테스트합니다.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from services.notification_service import NotificationService
from models.todo import Todo
from models.subtask import SubTask


class TestNotificationService(unittest.TestCase):
    """NotificationService 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # Mock TodoService 생성
        self.mock_todo_service = Mock()
        self.notification_service = NotificationService(self.mock_todo_service)
        
        # 테스트용 할일 데이터 생성
        now = datetime.now()
        
        # 지연된 할일
        self.overdue_todo = Todo(
            id=1,
            title="지연된 할일",
            created_at=now - timedelta(days=5),
            folder_path="test_folder_1",
            due_date=now - timedelta(days=2)
        )
        
        # 오늘 마감 할일
        self.due_today_todo = Todo(
            id=2,
            title="오늘 마감 할일",
            created_at=now - timedelta(days=1),
            folder_path="test_folder_2",
            due_date=now.replace(hour=23, minute=59, second=59)
        )
        
        # 긴급한 할일 (내일 마감)
        self.urgent_todo = Todo(
            id=3,
            title="긴급한 할일",
            created_at=now - timedelta(days=1),
            folder_path="test_folder_3",
            due_date=now + timedelta(hours=12)
        )
        
        # 완료된 할일 (하위 작업이 있어야 완료로 인식됨)
        self.completed_todo = Todo(
            id=4,
            title="완료된 할일",
            created_at=now - timedelta(days=3),
            folder_path="test_folder_4",
            due_date=now - timedelta(days=1),
            completed_at=now - timedelta(hours=2)
        )
        # 완료된 하위 작업 추가
        completed_subtask = SubTask(
            id=1,
            todo_id=4,
            title="완료된 하위 작업",
            is_completed=True,
            created_at=now - timedelta(days=2),
            completed_at=now - timedelta(hours=2)
        )
        self.completed_todo.add_subtask(completed_subtask)
        
        # 일반 할일 (목표 날짜 없음)
        self.normal_todo = Todo(
            id=5,
            title="일반 할일",
            created_at=now,
            folder_path="test_folder_5"
        )
    
    def test_get_overdue_todos(self):
        """지연된 할일 조회 테스트"""
        # Mock 설정
        self.mock_todo_service.get_overdue_todos.return_value = [self.overdue_todo]
        
        # 테스트 실행
        result = self.notification_service.get_overdue_todos()
        
        # 검증
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "지연된 할일")
        self.mock_todo_service.get_overdue_todos.assert_called_once()
    
    def test_get_due_today_todos(self):
        """오늘 마감 할일 조회 테스트"""
        # Mock 설정
        self.mock_todo_service.get_due_today_todos.return_value = [self.due_today_todo]
        
        # 테스트 실행
        result = self.notification_service.get_due_today_todos()
        
        # 검증
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "오늘 마감 할일")
        self.mock_todo_service.get_due_today_todos.assert_called_once()
    
    def test_get_urgent_todos(self):
        """긴급한 할일 조회 테스트"""
        # Mock 설정
        self.mock_todo_service.get_urgent_todos.return_value = [self.urgent_todo]
        
        # 테스트 실행
        result = self.notification_service.get_urgent_todos()
        
        # 검증
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "긴급한 할일")
        self.mock_todo_service.get_urgent_todos.assert_called_once_with(hours=24)
    
    def test_should_show_startup_notification_with_overdue(self):
        """지연된 할일이 있을 때 시작 알림 표시 여부 테스트"""
        # Mock 설정
        self.mock_todo_service.get_overdue_todos.return_value = [self.overdue_todo]
        self.mock_todo_service.get_due_today_todos.return_value = []
        
        # 테스트 실행
        result = self.notification_service.should_show_startup_notification()
        
        # 검증
        self.assertTrue(result)
    
    def test_should_show_startup_notification_with_due_today(self):
        """오늘 마감 할일이 있을 때 시작 알림 표시 여부 테스트"""
        # Mock 설정
        self.mock_todo_service.get_overdue_todos.return_value = []
        self.mock_todo_service.get_due_today_todos.return_value = [self.due_today_todo]
        
        # 테스트 실행
        result = self.notification_service.should_show_startup_notification()
        
        # 검증
        self.assertTrue(result)
    
    def test_should_show_startup_notification_no_urgent(self):
        """긴급한 할일이 없을 때 시작 알림 표시 안함 테스트"""
        # Mock 설정
        self.mock_todo_service.get_overdue_todos.return_value = []
        self.mock_todo_service.get_due_today_todos.return_value = []
        
        # 테스트 실행
        result = self.notification_service.should_show_startup_notification()
        
        # 검증
        self.assertFalse(result)
    
    def test_get_startup_notification_message_with_both(self):
        """지연된 할일과 오늘 마감 할일이 모두 있을 때 알림 메시지 테스트"""
        # Mock 설정
        self.mock_todo_service.get_overdue_todos.return_value = [self.overdue_todo]
        self.mock_todo_service.get_due_today_todos.return_value = [self.due_today_todo]
        
        # 테스트 실행
        result = self.notification_service.get_startup_notification_message()
        
        # 검증
        self.assertIn("지연된 할일이 1개", result)
        self.assertIn("오늘 마감인 할일이 1개", result)
        self.assertIn("⚠️", result)
        self.assertIn("📅", result)
    
    def test_get_startup_notification_message_no_urgent(self):
        """긴급한 할일이 없을 때 알림 메시지 테스트"""
        # Mock 설정
        self.mock_todo_service.get_overdue_todos.return_value = []
        self.mock_todo_service.get_due_today_todos.return_value = []
        
        # 테스트 실행
        result = self.notification_service.get_startup_notification_message()
        
        # 검증
        self.assertEqual(result, "모든 할일이 정상적으로 관리되고 있습니다.")
    
    def test_get_status_bar_summary(self):
        """상태바 요약 정보 테스트"""
        # Mock 설정
        all_todos = [
            self.overdue_todo, 
            self.due_today_todo, 
            self.urgent_todo, 
            self.completed_todo, 
            self.normal_todo
        ]
        
        self.mock_todo_service.get_all_todos.return_value = all_todos
        self.mock_todo_service.get_overdue_todos.return_value = [self.overdue_todo]
        self.mock_todo_service.get_due_today_todos.return_value = [self.due_today_todo]
        self.mock_todo_service.get_urgent_todos.return_value = [self.urgent_todo]
        
        # 테스트 실행
        result = self.notification_service.get_status_bar_summary()
        
        # 검증
        expected = {
            'overdue': 1,
            'due_today': 1,
            'urgent': 1,
            'total': 5,
            'completed': 1  # completed_todo만 완료됨
        }
        self.assertEqual(result, expected)
    
    def test_get_detailed_notification_info(self):
        """상세 알림 정보 테스트"""
        # Mock 설정
        self.mock_todo_service.get_overdue_todos.return_value = [self.overdue_todo]
        self.mock_todo_service.get_due_today_todos.return_value = [self.due_today_todo]
        self.mock_todo_service.get_urgent_todos.return_value = [self.urgent_todo]
        
        # 테스트 실행
        result = self.notification_service.get_detailed_notification_info()
        
        # 검증
        expected = {
            'overdue': ["지연된 할일"],
            'due_today': ["오늘 마감 할일"],
            'urgent': ["긴급한 할일"]
        }
        self.assertEqual(result, expected)
    
    def test_get_notification_priority(self):
        """알림 우선순위 테스트"""
        # 지연된 할일이 있는 경우 (high)
        self.mock_todo_service.get_overdue_todos.return_value = [self.overdue_todo]
        self.mock_todo_service.get_due_today_todos.return_value = []
        result = self.notification_service.get_notification_priority()
        self.assertEqual(result, 'high')
        
        # 오늘 마감 할일만 있는 경우 (medium)
        self.mock_todo_service.get_overdue_todos.return_value = []
        self.mock_todo_service.get_due_today_todos.return_value = [self.due_today_todo]
        result = self.notification_service.get_notification_priority()
        self.assertEqual(result, 'medium')
        
        # 긴급한 할일만 있는 경우 (low)
        self.mock_todo_service.get_overdue_todos.return_value = []
        self.mock_todo_service.get_due_today_todos.return_value = []
        self.mock_todo_service.get_urgent_todos.return_value = [self.urgent_todo]
        result = self.notification_service.get_notification_priority()
        self.assertEqual(result, 'low')
        
        # 긴급한 할일이 없는 경우 (none)
        self.mock_todo_service.get_overdue_todos.return_value = []
        self.mock_todo_service.get_due_today_todos.return_value = []
        self.mock_todo_service.get_urgent_todos.return_value = []
        result = self.notification_service.get_notification_priority()
        self.assertEqual(result, 'none')
    
    def test_format_status_bar_text(self):
        """상태바 텍스트 포맷팅 테스트"""
        # Mock 설정
        all_todos = [self.overdue_todo, self.due_today_todo, self.completed_todo]
        
        self.mock_todo_service.get_all_todos.return_value = all_todos
        self.mock_todo_service.get_overdue_todos.return_value = [self.overdue_todo]
        self.mock_todo_service.get_due_today_todos.return_value = [self.due_today_todo]
        self.mock_todo_service.get_urgent_todos.return_value = []
        
        # 테스트 실행
        result = self.notification_service.format_status_bar_text()
        
        # 검증
        self.assertIn("지연: 1개", result)
        self.assertIn("오늘 마감: 1개", result)
        self.assertIn("전체: 3개", result)
        self.assertIn("완료율: 33%", result)
    
    def test_get_todos_with_overdue_subtasks(self):
        """지연된 하위 작업이 있는 할일 조회 테스트"""
        # Mock 설정
        todo_with_overdue_subtask = self.normal_todo
        self.mock_todo_service.get_todos_with_overdue_subtasks.return_value = [todo_with_overdue_subtask]
        
        # 테스트 실행
        result = self.notification_service.get_todos_with_overdue_subtasks()
        
        # 검증
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], todo_with_overdue_subtask)
        self.mock_todo_service.get_todos_with_overdue_subtasks.assert_called_once()
    
    def test_get_notification_summary_for_period(self):
        """기간별 알림 요약 정보 테스트"""
        # Mock 설정
        now = datetime.now()
        todos_in_period = [
            self.due_today_todo,  # 오늘
            self.urgent_todo      # 내일
        ]
        
        self.mock_todo_service.get_todos_by_due_date.return_value = todos_in_period
        
        # 테스트 실행 (3일 기간)
        result = self.notification_service.get_notification_summary_for_period(days=3)
        
        # 검증
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 4)  # 0일부터 3일까지 (4개)
        
        # 오늘 날짜 키가 있는지 확인
        today_key = now.strftime("%Y-%m-%d")
        self.assertIn(today_key, result)


if __name__ == '__main__':
    unittest.main()