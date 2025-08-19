"""
Todo 모델의 목표 날짜 관련 메서드 테스트

Task 3: Todo 모델에 목표 날짜 관련 메서드 추가 검증
"""

import unittest
import os
import sys
from datetime import datetime, timedelta

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.todo import Todo
from models.subtask import SubTask


class TestTodoDueDateMethods(unittest.TestCase):
    """Todo 모델의 목표 날짜 관련 메서드 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.todo = Todo(
            id=1,
            title="테스트 할일",
            created_at=datetime.now(),
            folder_path="test_folder"
        )
        
        # 하위 작업 추가
        self.subtask1 = SubTask(
            id=1,
            todo_id=1,
            title="하위 작업 1",
            created_at=datetime.now()
        )
        self.subtask2 = SubTask(
            id=2,
            todo_id=1,
            title="하위 작업 2",
            created_at=datetime.now()
        )
        self.todo.add_subtask(self.subtask1)
        self.todo.add_subtask(self.subtask2)
    
    def test_set_and_get_due_date(self):
        """목표 날짜 설정 및 조회 테스트"""
        # 초기 상태: 목표 날짜 없음
        self.assertIsNone(self.todo.get_due_date())
        
        # 목표 날짜 설정
        due_date = datetime.now() + timedelta(days=3)
        self.todo.set_due_date(due_date)
        
        # 목표 날짜 확인
        self.assertEqual(self.todo.get_due_date(), due_date)
        self.assertEqual(self.todo.due_date, due_date)
        
        # 목표 날짜 제거
        self.todo.set_due_date(None)
        self.assertIsNone(self.todo.get_due_date())
    
    def test_is_overdue(self):
        """지연 상태 확인 테스트"""
        # 목표 날짜가 없으면 지연되지 않음
        self.assertFalse(self.todo.is_overdue())
        
        # 미래 날짜 설정 - 지연되지 않음
        future_date = datetime.now() + timedelta(hours=1)
        self.todo.set_due_date(future_date)
        self.assertFalse(self.todo.is_overdue())
        
        # 과거 날짜 설정 - 지연됨
        past_date = datetime.now() - timedelta(hours=1)
        self.todo.set_due_date(past_date)
        self.assertTrue(self.todo.is_overdue())
        
        # 완료된 할일은 지연되지 않음
        self.todo.mark_completed()
        self.assertFalse(self.todo.is_overdue())
    
    def test_get_urgency_level(self):
        """긴급도 레벨 테스트"""
        # 목표 날짜가 없으면 normal
        self.assertEqual(self.todo.get_urgency_level(), 'normal')
        
        # 과거 날짜 - overdue
        past_date = datetime.now() - timedelta(hours=1)
        self.todo.set_due_date(past_date)
        self.assertEqual(self.todo.get_urgency_level(), 'overdue')
        
        # 24시간 이내 - urgent
        urgent_date = datetime.now() + timedelta(hours=12)
        self.todo.set_due_date(urgent_date)
        self.assertEqual(self.todo.get_urgency_level(), 'urgent')
        
        # 3일 이내 - warning
        warning_date = datetime.now() + timedelta(days=2)
        self.todo.set_due_date(warning_date)
        self.assertEqual(self.todo.get_urgency_level(), 'warning')
        
        # 그 외 - normal
        normal_date = datetime.now() + timedelta(days=7)
        self.todo.set_due_date(normal_date)
        self.assertEqual(self.todo.get_urgency_level(), 'normal')
        
        # 완료된 할일은 normal
        self.todo.mark_completed()
        self.assertEqual(self.todo.get_urgency_level(), 'normal')
    
    def test_get_time_remaining_text(self):
        """남은 시간 텍스트 테스트"""
        # 목표 날짜가 없으면 빈 문자열
        self.assertEqual(self.todo.get_time_remaining_text(), "")
        
        # 미래 날짜 설정
        future_date = datetime.now() + timedelta(days=3)
        self.todo.set_due_date(future_date)
        time_text = self.todo.get_time_remaining_text()
        self.assertIn("D-", time_text)
        
        # 완료된 할일
        self.todo.mark_completed()
        completed_text = self.todo.get_time_remaining_text()
        self.assertIn("완료:", completed_text)
    
    def test_mark_completed(self):
        """완료 표시 테스트"""
        # 초기 상태: 미완료
        self.assertFalse(self.todo.is_completed())
        self.assertIsNone(self.todo.completed_at)
        self.assertFalse(self.subtask1.is_completed)
        self.assertFalse(self.subtask2.is_completed)
        
        # 완료 표시
        self.todo.mark_completed()
        
        # 할일과 모든 하위 작업이 완료됨
        self.assertTrue(self.todo.is_completed())
        self.assertIsNotNone(self.todo.completed_at)
        self.assertTrue(self.subtask1.is_completed)
        self.assertTrue(self.subtask2.is_completed)
        self.assertIsNotNone(self.subtask1.completed_at)
        self.assertIsNotNone(self.subtask2.completed_at)
    
    def test_mark_uncompleted(self):
        """미완료 표시 테스트"""
        # 먼저 완료 상태로 만들기
        self.todo.mark_completed()
        self.assertTrue(self.todo.is_completed())
        
        # 미완료로 변경
        self.todo.mark_uncompleted()
        
        # 할일과 모든 하위 작업이 미완료됨
        self.assertFalse(self.todo.is_completed())
        self.assertIsNone(self.todo.completed_at)
        self.assertFalse(self.subtask1.is_completed)
        self.assertFalse(self.subtask2.is_completed)
        self.assertIsNone(self.subtask1.completed_at)
        self.assertIsNone(self.subtask2.completed_at)
    
    def test_has_overdue_subtasks(self):
        """지연된 하위 작업 확인 테스트"""
        # 초기 상태: 지연된 하위 작업 없음
        self.assertFalse(self.todo.has_overdue_subtasks())
        
        # 하위 작업에 과거 목표 날짜 설정
        past_date = datetime.now() - timedelta(hours=1)
        self.subtask1.due_date = past_date
        
        # 지연된 하위 작업 있음
        self.assertTrue(self.todo.has_overdue_subtasks())
        
        # 하위 작업 완료 시 지연되지 않음
        self.subtask1.is_completed = True
        self.assertFalse(self.todo.has_overdue_subtasks())
    
    def test_validate_subtask_due_date(self):
        """하위 작업 목표 날짜 유효성 검사 테스트"""
        # 할일에 목표 날짜 설정
        todo_due_date = datetime.now() + timedelta(days=5)
        self.todo.set_due_date(todo_due_date)
        
        # 유효한 하위 작업 목표 날짜 (할일보다 빠름)
        valid_subtask_date = datetime.now() + timedelta(days=3)
        is_valid, message = self.todo.validate_subtask_due_date(valid_subtask_date)
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
        
        # 무효한 하위 작업 목표 날짜 (할일보다 늦음)
        invalid_subtask_date = datetime.now() + timedelta(days=7)
        is_valid, message = self.todo.validate_subtask_due_date(invalid_subtask_date)
        self.assertFalse(is_valid)
        self.assertIn("상위 할일의 목표 날짜", message)
    
    def test_get_time_remaining(self):
        """남은 시간 계산 테스트"""
        # 목표 날짜가 없으면 None
        self.assertIsNone(self.todo.get_time_remaining())
        
        # 미래 날짜 설정
        future_date = datetime.now() + timedelta(days=3, hours=2)
        self.todo.set_due_date(future_date)
        
        time_remaining = self.todo.get_time_remaining()
        self.assertIsNotNone(time_remaining)
        self.assertGreater(time_remaining.total_seconds(), 0)
        
        # 과거 날짜 설정
        past_date = datetime.now() - timedelta(hours=1)
        self.todo.set_due_date(past_date)
        
        time_remaining = self.todo.get_time_remaining()
        self.assertIsNotNone(time_remaining)
        self.assertLess(time_remaining.total_seconds(), 0)


if __name__ == '__main__':
    unittest.main()