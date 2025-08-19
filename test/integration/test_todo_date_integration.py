"""
Todo 모델과 DateService 통합 테스트

Task 3 검증: Todo 모델의 목표 날짜 메서드들이 DateService와 올바르게 연동되는지 확인
"""

import unittest
import os
import sys
from datetime import datetime, timedelta

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.todo import Todo
from models.subtask import SubTask
from services.date_service import DateService


class TestTodoDateIntegration(unittest.TestCase):
    """Todo 모델과 DateService 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.todo = Todo(
            id=1,
            title="통합 테스트 할일",
            created_at=datetime.now(),
            folder_path="test_folder"
        )
    
    def test_urgency_level_integration(self):
        """긴급도 레벨 통합 테스트"""
        # DateService와 Todo 모델의 긴급도 계산이 일치하는지 확인
        
        # 과거 날짜
        past_date = datetime.now() - timedelta(hours=1)
        self.todo.set_due_date(past_date)
        
        todo_urgency = self.todo.get_urgency_level()
        service_urgency = DateService.get_urgency_level(past_date)
        self.assertEqual(todo_urgency, service_urgency)
        self.assertEqual(todo_urgency, 'overdue')
        
        # 24시간 이내
        urgent_date = datetime.now() + timedelta(hours=12)
        self.todo.set_due_date(urgent_date)
        
        todo_urgency = self.todo.get_urgency_level()
        service_urgency = DateService.get_urgency_level(urgent_date)
        self.assertEqual(todo_urgency, service_urgency)
        self.assertEqual(todo_urgency, 'urgent')
    
    def test_time_remaining_text_integration(self):
        """남은 시간 텍스트 통합 테스트"""
        # DateService와 Todo 모델의 시간 텍스트가 일치하는지 확인
        
        future_date = datetime.now() + timedelta(days=2)
        self.todo.set_due_date(future_date)
        
        todo_text = self.todo.get_time_remaining_text()
        service_text = DateService.get_time_remaining_text(future_date)
        self.assertEqual(todo_text, service_text)
        
        # 완료된 경우
        self.todo.mark_completed()
        completed_text = self.todo.get_time_remaining_text()
        service_completed_text = DateService.get_time_remaining_text(future_date, self.todo.completed_at)
        self.assertEqual(completed_text, service_completed_text)
        self.assertIn("완료:", completed_text)
    
    def test_subtask_validation_integration(self):
        """하위 작업 유효성 검사 통합 테스트"""
        # Todo 모델과 DateService의 유효성 검사가 일치하는지 확인
        
        todo_due_date = datetime.now() + timedelta(days=5)
        self.todo.set_due_date(todo_due_date)
        
        # 유효한 하위 작업 날짜
        valid_date = datetime.now() + timedelta(days=3)
        todo_result = self.todo.validate_subtask_due_date(valid_date)
        service_result = DateService.validate_due_date(valid_date, todo_due_date)
        self.assertEqual(todo_result, service_result)
        self.assertTrue(todo_result[0])
        
        # 무효한 하위 작업 날짜
        invalid_date = datetime.now() + timedelta(days=7)
        todo_result = self.todo.validate_subtask_due_date(invalid_date)
        service_result = DateService.validate_due_date(invalid_date, todo_due_date)
        self.assertEqual(todo_result, service_result)
        self.assertFalse(todo_result[0])
    
    def test_serialization_with_due_dates(self):
        """목표 날짜가 포함된 직렬화/역직렬화 테스트"""
        # 목표 날짜 설정
        due_date = datetime.now() + timedelta(days=3)
        self.todo.set_due_date(due_date)
        
        # 하위 작업 추가
        subtask = SubTask(
            id=1,
            todo_id=1,
            title="하위 작업",
            due_date=datetime.now() + timedelta(days=2)
        )
        self.todo.add_subtask(subtask)
        
        # 직렬화
        todo_dict = self.todo.to_dict()
        self.assertIsNotNone(todo_dict['due_date'])
        self.assertIsNone(todo_dict['completed_at'])
        self.assertIsNotNone(todo_dict['subtasks'][0]['due_date'])
        
        # 역직렬화
        restored_todo = Todo.from_dict(todo_dict)
        self.assertEqual(restored_todo.due_date, due_date)
        self.assertEqual(restored_todo.subtasks[0].due_date, subtask.due_date)
        
        # 메서드들이 정상 작동하는지 확인
        self.assertEqual(restored_todo.get_urgency_level(), self.todo.get_urgency_level())
        self.assertEqual(restored_todo.get_time_remaining_text(), self.todo.get_time_remaining_text())
    
    def test_completion_workflow(self):
        """완료 워크플로우 테스트"""
        # 목표 날짜 설정
        due_date = datetime.now() + timedelta(days=1)
        self.todo.set_due_date(due_date)
        
        # 하위 작업 추가
        subtask1 = SubTask(id=1, todo_id=1, title="하위 작업 1")
        subtask2 = SubTask(id=2, todo_id=1, title="하위 작업 2")
        self.todo.add_subtask(subtask1)
        self.todo.add_subtask(subtask2)
        
        # 초기 상태: 미완료, 긴급도 있음
        self.assertFalse(self.todo.is_completed())
        self.assertEqual(self.todo.get_urgency_level(), 'urgent')
        
        # 완료 처리
        self.todo.mark_completed()
        
        # 완료 후: 모든 하위 작업 완료, 긴급도 normal
        self.assertTrue(self.todo.is_completed())
        self.assertTrue(subtask1.is_completed)
        self.assertTrue(subtask2.is_completed)
        self.assertEqual(self.todo.get_urgency_level(), 'normal')
        self.assertIn("완료:", self.todo.get_time_remaining_text())
        
        # 미완료로 되돌리기
        self.todo.mark_uncompleted()
        
        # 미완료 후: 모든 하위 작업 미완료, 긴급도 복원
        self.assertFalse(self.todo.is_completed())
        self.assertFalse(subtask1.is_completed)
        self.assertFalse(subtask2.is_completed)
        self.assertEqual(self.todo.get_urgency_level(), 'urgent')


if __name__ == '__main__':
    unittest.main()