"""
SubTask 모델의 목표 날짜 관련 메서드 테스트

Requirements 7.1, 7.4, 5.4 검증:
- 하위 작업에 목표 날짜 설정
- 완료 상태 변경 시 completed_at 필드 업데이트  
- 긴급도 및 시간 표시 메서드 구현
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import datetime, timedelta
from models.subtask import SubTask


class TestSubTaskDueDate(unittest.TestCase):
    """SubTask 목표 날짜 관련 기능 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.subtask = SubTask(
            id=1,
            todo_id=1,
            title="테스트 하위 작업",
            is_completed=False,
            created_at=datetime.now()
        )
    
    def test_set_and_get_due_date(self):
        """목표 날짜 설정 및 조회 테스트 - Requirements 7.1"""
        # 목표 날짜 설정
        due_date = datetime.now() + timedelta(days=3)
        self.subtask.set_due_date(due_date)
        
        # 목표 날짜 조회
        self.assertEqual(self.subtask.get_due_date(), due_date)
        self.assertEqual(self.subtask.due_date, due_date)
        
        # 목표 날짜 제거
        self.subtask.set_due_date(None)
        self.assertIsNone(self.subtask.get_due_date())
    
    def test_is_overdue(self):
        """지연 상태 확인 테스트 - Requirements 7.4"""
        # 목표 날짜가 없는 경우
        self.assertFalse(self.subtask.is_overdue())
        
        # 미래 날짜 설정
        future_date = datetime.now() + timedelta(hours=1)
        self.subtask.set_due_date(future_date)
        self.assertFalse(self.subtask.is_overdue())
        
        # 과거 날짜 설정
        past_date = datetime.now() - timedelta(hours=1)
        self.subtask.set_due_date(past_date)
        self.assertTrue(self.subtask.is_overdue())
        
        # 완료된 작업은 지연되지 않음
        self.subtask.mark_completed()
        self.assertFalse(self.subtask.is_overdue())
    
    def test_get_urgency_level(self):
        """긴급도 레벨 테스트 - Requirements 7.4"""
        # 완료된 작업은 normal
        self.subtask.mark_completed()
        self.assertEqual(self.subtask.get_urgency_level(), 'normal')
        
        # 미완료 작업으로 변경
        self.subtask.mark_uncompleted()
        
        # 목표 날짜가 없는 경우
        self.assertEqual(self.subtask.get_urgency_level(), 'normal')
        
        # 지연된 경우
        past_date = datetime.now() - timedelta(hours=1)
        self.subtask.set_due_date(past_date)
        self.assertEqual(self.subtask.get_urgency_level(), 'overdue')
        
        # 24시간 이내
        urgent_date = datetime.now() + timedelta(hours=12)
        self.subtask.set_due_date(urgent_date)
        self.assertEqual(self.subtask.get_urgency_level(), 'urgent')
        
        # 3일 이내
        warning_date = datetime.now() + timedelta(days=2)
        self.subtask.set_due_date(warning_date)
        self.assertEqual(self.subtask.get_urgency_level(), 'warning')
        
        # 일반
        normal_date = datetime.now() + timedelta(days=7)
        self.subtask.set_due_date(normal_date)
        self.assertEqual(self.subtask.get_urgency_level(), 'normal')
    
    def test_get_time_remaining(self):
        """남은 시간 계산 테스트"""
        # 목표 날짜가 없는 경우
        self.assertIsNone(self.subtask.get_time_remaining())
        
        # 미래 날짜
        future_date = datetime.now() + timedelta(hours=24)
        self.subtask.set_due_date(future_date)
        remaining = self.subtask.get_time_remaining()
        self.assertIsNotNone(remaining)
        self.assertGreater(remaining.total_seconds(), 0)
        
        # 과거 날짜
        past_date = datetime.now() - timedelta(hours=1)
        self.subtask.set_due_date(past_date)
        remaining = self.subtask.get_time_remaining()
        self.assertIsNotNone(remaining)
        self.assertLess(remaining.total_seconds(), 0)
    
    def test_get_time_remaining_text(self):
        """시간 표시 텍스트 테스트 - Requirements 5.4"""
        # 목표 날짜가 없는 경우
        self.assertEqual(self.subtask.get_time_remaining_text(), "")
        
        # 완료된 경우
        self.subtask.mark_completed()
        due_date = datetime.now() + timedelta(days=1)
        self.subtask.set_due_date(due_date)
        text = self.subtask.get_time_remaining_text()
        self.assertIn("완료:", text)
        
        # 미완료 상태로 변경
        self.subtask.mark_uncompleted()
        
        # 지연된 경우
        past_date = datetime.now() - timedelta(hours=2)
        self.subtask.set_due_date(past_date)
        text = self.subtask.get_time_remaining_text()
        self.assertIn("지남", text)
        
        # 미래 날짜
        future_date = datetime.now() + timedelta(days=3)
        self.subtask.set_due_date(future_date)
        text = self.subtask.get_time_remaining_text()
        self.assertIn("D-", text)
    
    def test_mark_completed_and_uncompleted(self):
        """완료 상태 변경 테스트 - Requirements 7.4"""
        # 초기 상태
        self.assertFalse(self.subtask.is_completed)
        self.assertIsNone(self.subtask.completed_at)
        
        # 완료 처리
        self.subtask.mark_completed()
        self.assertTrue(self.subtask.is_completed)
        self.assertIsNotNone(self.subtask.completed_at)
        
        # 미완료 처리
        self.subtask.mark_uncompleted()
        self.assertFalse(self.subtask.is_completed)
        self.assertIsNone(self.subtask.completed_at)
    
    def test_toggle_completion_updates_completed_at(self):
        """토글 시 completed_at 업데이트 테스트 - Requirements 7.4"""
        # 초기 상태
        self.assertFalse(self.subtask.is_completed)
        self.assertIsNone(self.subtask.completed_at)
        
        # 완료로 토글
        self.subtask.toggle_completion()
        self.assertTrue(self.subtask.is_completed)
        self.assertIsNotNone(self.subtask.completed_at)
        
        # 미완료로 토글
        self.subtask.toggle_completion()
        self.assertFalse(self.subtask.is_completed)
        self.assertIsNone(self.subtask.completed_at)
    
    def test_serialization_with_due_date(self):
        """목표 날짜 포함 직렬화 테스트"""
        # 목표 날짜 설정
        due_date = datetime.now() + timedelta(days=1)
        self.subtask.set_due_date(due_date)
        self.subtask.mark_completed()
        
        # 직렬화
        data = self.subtask.to_dict()
        self.assertIn('due_date', data)
        self.assertIn('completed_at', data)
        self.assertIsNotNone(data['due_date'])
        self.assertIsNotNone(data['completed_at'])
        
        # 역직렬화
        restored_subtask = SubTask.from_dict(data)
        self.assertEqual(restored_subtask.due_date, due_date)
        self.assertIsNotNone(restored_subtask.completed_at)
        self.assertTrue(restored_subtask.is_completed)


if __name__ == '__main__':
    unittest.main()