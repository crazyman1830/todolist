"""
DateService 테스트 모듈

날짜 서비스의 긴급도 계산, 시간 표시 등 기능을 테스트합니다.
"""

import unittest
import os
import sys
from datetime import datetime, timedelta

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.date_service import DateService


class TestDateService(unittest.TestCase):
    """DateService 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.now = datetime.now()  # 현재 시간 사용
    
    def test_get_urgency_level_overdue(self):
        """지연된 할일의 긴급도 테스트"""
        # 1시간 전
        past_date = self.now - timedelta(hours=1)
        self.assertEqual(DateService.get_urgency_level(past_date), 'overdue')
        
        # 1일 전
        past_date = self.now - timedelta(days=1)
        self.assertEqual(DateService.get_urgency_level(past_date), 'overdue')
    
    def test_get_urgency_level_urgent(self):
        """긴급한 할일의 긴급도 테스트 (24시간 이내)"""
        # 1시간 후
        future_date = self.now + timedelta(hours=1)
        self.assertEqual(DateService.get_urgency_level(future_date), 'urgent')
        
        # 23시간 후
        future_date = self.now + timedelta(hours=23)
        self.assertEqual(DateService.get_urgency_level(future_date), 'urgent')
    
    def test_get_urgency_level_warning(self):
        """경고 수준 할일의 긴급도 테스트 (3일 이내)"""
        # 2일 후
        future_date = self.now + timedelta(days=2)
        self.assertEqual(DateService.get_urgency_level(future_date), 'warning')
        
        # 3일 후
        future_date = self.now + timedelta(days=3)
        self.assertEqual(DateService.get_urgency_level(future_date), 'warning')
    
    def test_get_urgency_level_normal(self):
        """일반 할일의 긴급도 테스트"""
        # 4일 후
        future_date = self.now + timedelta(days=4)
        self.assertEqual(DateService.get_urgency_level(future_date), 'normal')
        
        # 1주일 후
        future_date = self.now + timedelta(days=7)
        self.assertEqual(DateService.get_urgency_level(future_date), 'normal')
    
    def test_get_urgency_level_none(self):
        """목표 날짜가 없는 경우 테스트"""
        self.assertEqual(DateService.get_urgency_level(None), 'normal')
    
    def test_get_time_remaining_text_completed(self):
        """완료된 할일의 시간 표시 테스트"""
        due_date = self.now + timedelta(days=1)
        completed_at = self.now - timedelta(hours=1)
        
        result = DateService.get_time_remaining_text(due_date, completed_at)
        self.assertIn("완료:", result)
    
    def test_get_time_remaining_text_overdue(self):
        """지연된 할일의 시간 표시 테스트"""
        # 2일 지남
        overdue_date = self.now - timedelta(days=2)
        result = DateService.get_time_remaining_text(overdue_date)
        self.assertEqual(result, "2일 지남")
        
        # 3시간 지남
        overdue_date = self.now - timedelta(hours=3)
        result = DateService.get_time_remaining_text(overdue_date)
        self.assertEqual(result, "3시간 지남")
    
    def test_get_time_remaining_text_future(self):
        """미래 할일의 시간 표시 테스트"""
        # D-3
        future_date = self.now + timedelta(days=3)
        result = DateService.get_time_remaining_text(future_date)
        self.assertEqual(result, "D-3")
        
        # 3시간 후
        future_date = self.now + timedelta(hours=3)
        result = DateService.get_time_remaining_text(future_date)
        self.assertEqual(result, "3시간 후")
        
        # 30분 후
        future_date = self.now + timedelta(minutes=30)
        result = DateService.get_time_remaining_text(future_date)
        self.assertEqual(result, "30분 후")
    
    def test_format_due_date_relative(self):
        """상대적 날짜 포맷팅 테스트"""
        # 오늘
        today = datetime.now().replace(hour=18, minute=30, second=0, microsecond=0)
        result = DateService.format_due_date(today, 'relative')
        self.assertEqual(result, "오늘 18:30")
        
        # 내일
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=18, minute=30, second=0, microsecond=0)
        result = DateService.format_due_date(tomorrow, 'relative')
        self.assertEqual(result, "내일 18:30")
    
    def test_is_same_day(self):
        """같은 날 확인 테스트"""
        date1 = datetime(2025, 1, 15, 10, 0, 0)
        date2 = datetime(2025, 1, 15, 20, 0, 0)
        date3 = datetime(2025, 1, 16, 10, 0, 0)
        
        self.assertTrue(DateService.is_same_day(date1, date2))
        self.assertFalse(DateService.is_same_day(date1, date3))
    
    def test_get_quick_date_options(self):
        """빠른 날짜 선택 옵션 테스트"""
        options = DateService.get_quick_date_options()
        
        self.assertIn("오늘", options)
        self.assertIn("내일", options)
        self.assertIn("이번 주말", options)
        self.assertIsInstance(options["오늘"], datetime)
    
    def test_validate_due_date_valid(self):
        """유효한 목표 날짜 검증 테스트"""
        future_date = datetime.now() + timedelta(days=1)
        is_valid, message = DateService.validate_due_date(future_date)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
    
    def test_validate_due_date_past(self):
        """과거 목표 날짜 검증 테스트"""
        past_date = datetime.now() - timedelta(days=1)
        is_valid, message = DateService.validate_due_date(past_date)
        
        self.assertFalse(is_valid)
        self.assertIn("과거", message)
    
    def test_validate_due_date_with_parent(self):
        """상위 할일 목표 날짜와 비교 검증 테스트"""
        parent_due = datetime.now() + timedelta(days=5)
        child_due = datetime.now() + timedelta(days=7)  # 상위보다 늦음
        
        is_valid, message = DateService.validate_due_date(child_due, parent_due)
        
        self.assertFalse(is_valid)
        self.assertIn("빨라야", message)
    
    def test_get_date_filter_ranges(self):
        """날짜 필터 범위 테스트"""
        ranges = DateService.get_date_filter_ranges()
        
        self.assertIn("오늘", ranges)
        self.assertIn("이번 주", ranges)
        self.assertIn("지연됨", ranges)
        
        # 각 범위가 튜플인지 확인
        for range_name, (start, end) in ranges.items():
            self.assertIsInstance(start, datetime)
            self.assertIsInstance(end, datetime)
            self.assertLessEqual(start, end)


if __name__ == '__main__':
    unittest.main()